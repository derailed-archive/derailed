defmodule Derailed.WebSocket do
  @moduledoc """
  Process dedicated to handling WebSocket connections to the Gateway.
  """
  @behaviour :cowboy_websocket
  require Logger

  # non-process functions
  @spec validate_message(map(), map()) :: :ok | {:error, term()}
  defp validate_message(schema, message) do
    Logger.debug("Validating schema #{inspect(schema)} for #{inspect(message)}")
    scheme = schema |> ExJsonSchema.Schema.resolve()

    case ExJsonSchema.Validator.validate(scheme, message) do
      :ok -> :ok
      {:error, reason} -> {:error, reason}
    end
  end

  defp map_op(op) do
    %{
      # 0 => :dispatch
      # 1 => :hello,
      2 => :identify,
      3 => :resume,
      4 => :ping
      # 5 => :ack,
    }[op]
  end

  defp get_hb_interval do
    Enum.random(42_000..48_000)
  end

  @spec hb_timer(non_neg_integer()) :: reference()
  defp hb_timer(time) do
    :erlang.send_after(time + 2000, self(), :check_heartbeat)
  end

  @spec encode(struct(), :zlib.zstream() | nil) :: binary
  defp encode(term, compressor) do
    Logger.debug("Encoding #{inspect(term)} using zlib compressor #{inspect(compressor)}")
    term = Derailed.Utilities.struct_to_map(term)

    inp = Jsonrs.encode!(term)

    if compressor != nil do
      :zlib.deflate(compressor, inp, :sync)
    else
      inp
    end
  end

  @spec uncode(struct(), :zlib.zstream() | nil) :: {:binary, binary()} | {:text, binary()}
  defp uncode(term, compressor) do
    res = encode(term, compressor)

    if compressor != nil do
      {:binary, res}
    else
      {:text, res}
    end
  end

  @spec authorize_token(String.t()) :: {:ok, map(), map()} | {:error, term()}
  defp authorize_token(token) do
    # TODO: handle this error ({:error, _reason})
    device_id = Derailed.Token.get_device_id(token)

    case Postgrex.prepare_execute(:db, "get_device", "SELECT * FROM devices WHERE id = $1;", [
           device_id
         ]) do
      {:ok, _query, result} ->
        device = Derailed.Utilities.map!(result)
        user_id = Map.get(device, "user_id")

        {_query, result} =
          Postgrex.prepare_execute!(:db, "get_user", "SELECT * FROM users WHERE id = $1", [
            user_id
          ])

        user = Derailed.Utilities.map!(result)
        # immediately drop the password
        user = Map.delete(user, "password")
        {:ok, user, device}

      {:error, reason} ->
        {:error, reason}
    end
  end

  @spec make_ready(String.t()) :: {:ok, Derailed.Payload.Ready} | {:error, term()}
  defp make_ready(token) do
    ready_id = Derailed.Token.make_ulid()
    Logger.debug("[ready-#{inspect(ready_id)}] Acquiring ready for #{inspect(token)}")

    case authorize_token(token) do
      {:ok, user, _device} ->
        user_id = Map.get(user, "id")

        Logger.debug(
          "[ready-#{inspect(ready_id)}] Querying ready data, completed device initialization"
        )

        {_query, guild_ids_result} =
          Postgrex.prepare_execute!(
            :db,
            "get_user_guild_ids",
            "SELECT id FROM guilds WHERE id IN (SELECT guild_id FROM guild_members WHERE user_id = $1);",
            [user_id]
          )

        {_query, read_state_result} =
          Postgrex.prepare_execute!(
            :db,
            "get_read_states",
            "SELECT * FROM read_states WHERE user_id = $1;",
            [user_id]
          )

        {_query, relationship_result} =
          Postgrex.prepare_execute!(
            :db,
            "get_relationships",
            "SELECT target_user_id, relation FROM relationships WHERE origin_user_id = $1;",
            [user_id]
          )

        Logger.debug("[ready-#{inspect(ready_id)}] Mapping respectively received query results")

        guild_ids = Derailed.Utilities.maps!(guild_ids_result)
        read_states = Derailed.Utilities.maps!(read_state_result)
        relationships = Derailed.Utilities.maps!(relationship_result)

        Logger.debug("[ready-#{inspect(ready_id)}] Starting initialization of Session")

        session_id = Derailed.Token.make_ulid()

        {:ok, session_pid} =
          GenRegistry.start(
            Derailed.Session,
            session_id,
            [
              session_id,
              user_id,
              guild_ids,
              self(),
              token
            ]
          )

        Derailed.Session.start(session_pid)

        Logger.debug("[ready-#{inspect(ready_id)}] Session started")
        Logger.debug("[ready-#{inspect(ready_id)}] Ready completed.")

        {:ok,
         %Derailed.Payload.Ready{
           session_id: session_id,
           user: user,
           guild_ids: guild_ids,
           read_states: read_states,
           relationships: relationships
         }, session_id, session_pid}

      {:error, _reason} ->
        {:error, :invalid_token}
    end
  end

  # cowboy functions

  def init(req, _state) do
    {:cowboy_websocket, req, %{}, %{"compress" => true}}
  end

  def websocket_init(_state) do
    heartbeat_interval = get_hb_interval()
    heartbeat_ref = hb_timer(heartbeat_interval)

    {
      :reply,
      uncode(
        %Derailed.Payload.Base{
          op: 1,
          s: 0,
          d: %Derailed.Payload.Hello{
            heartbeat_interval: heartbeat_interval
          }
        },
        nil
      ),
      # TODO: move intents and presence to Session for more persistance on resumes.
      %State{
        session_id: nil,
        session_pid: nil,
        user_id: nil,
        # TODO: implement (intents)
        intents: 0,
        sequence: 0,
        zlib_enabled: false,
        heartbeat_interval: heartbeat_interval,
        heartbeat_ref: heartbeat_ref,
        heartbeat_cycle_finished: false,
        presence: nil,
        compressor: nil
      }
    }
  end

  # TODO: rate limiting, 60 frames per minute.
  def websocket_handle({:text, content}, state) do
    case Jsonrs.decode(content) do
      {:ok, message} ->
        if not is_map(message) do
          {:close, 3000, "Frames sent must be maps"}
        end

        op_code = Map.get(message, "op")

        if op_code != nil or not is_integer(op_code) do
          {:close, 3001, "Invalid Op Code"}
        end

        op({map_op(op_code), message}, state)

      {:error, _reason} ->
        {:close, 3002, "Invalid JSON payload sent"}
    end
  end

  def websocket_handle(_any_frame, state) do
    {:ok, state}
  end

  def websocket_info(:check_heartbeat, state) do
    Logger.debug("Checking user heartbeat")

    :zlib.deflate(Map.get(state, "compressor"), <<>>, :finish)
    :zlib.deflateEnd(Map.get(state, "compressor"))

    if not state.heartbeat_cycle_finished do
      {:close, 3003, "Heartbeat missed"}
    else
      :zlib.deflateInit(Map.get(state, "compressor"))
      {:ok, %{state | heartbeat_cycle_finished: false}}
    end
  end

  def websocket_info(message, state) do
    t = Map.get(message, "t")
    d = Map.get(message, "d")

    case t do
      "USER_DELETE" ->
        GenRegistry.stop(Derailed.Session, state.session_id)
        GenRegistry.stop(Derailed.Unify, state.user_id)
        {:close, 3004, "User has been deleted"}

      _ ->
        {:reply,
         uncode(
           %Derailed.Payload.EventBase{
             op: 0,
             t: t,
             s: state.sequence + 1,
             d: d
           },
           Map.get(state, "compressor")
         ), %{state | sequence: state.sequence + 1}}
    end
  end

  # op code handling

  defp op({:identify, message}, state) do
    # TODO: client & library information property collection.
    case validate_message(
           %{
             "type" => "object",
             "properties" => %{
               "op" => %{
                 "type" => "integer"
               },
               "d" => %{
                 "type" => "object",
                 "properties" => %{
                   "token" => %{
                     "type" => "string"
                   },
                   "compress" => %{
                     "type" => "boolean"
                   }
                 },
                 "required" => [
                   "token"
                 ]
               }
             },
             "required" => [
               "op",
               "d"
             ]
           },
           message
         ) do
      {:error, reason} ->
        {:close, 3005, Jsonrs.encode!(reason)}

      :ok ->
        data = Map.get(message, "d")
        token = Map.get(data, "token")
        compress = Map.get(data, "compress", false)

        state =
          if compress do
            z = :zlib.open()
            :zlib.deflateInit(z)
            Map.put(state, "compressor", z)
          else
            state
          end

        case make_ready(token) do
          {:ok, ready, session_id, session_pid} ->
            {:reply,
             uncode(
               %Derailed.Payload.EventBase{
                 op: 0,
                 t: "READY",
                 s: state.sequence + 1,
                 d: ready
               },
               Map.get(state, "compressor")
             ),
             %{
               state
               | session_id: session_id,
                 session_pid: session_pid,
                 sequence: state.sequence + 1
             }}

          {:error, reason} ->
            {:close, 3005, Jsonrs.encode!(reason)}
        end
    end
  end

  defp op({:resume, message}, state) do
    case validate_message(
           %{
             "type" => "object",
             "properties" => %{
               "op" => %{
                 "type" => "integer"
               },
               "d" => %{
                 "type" => "object",
                 "properties" => %{
                   "session_id" => %{
                     "type" => "string"
                   },
                   "token" => %{
                     "type" => "string"
                   }
                 },
                 "required" => [
                   "session_id",
                   "token"
                 ]
               }
             },
             "required" => [
               "op",
               "d"
             ]
           },
           message
         ) do
      {:error, reason} ->
        Logger.error(inspect(reason))
        {:close, 3005, Jsonrs.encode!(reason)}

      :ok ->
        case GenRegistry.lookup(Derailed.Session, message.session_id) do
          {:error, :not_found} ->
            {:close, 3006, "Session does not exist"}

          {:ok, session_pid} ->
            if not Derailed.Session.is_token?(session_pid, message.token) do
              {:close, 3007, "Incorrect resume token"}
            else
              case Derailed.Session.resume(session_pid) do
                :ok ->
                  {:ok, %{state | session_id: message.session_id, session_pid: session_pid}}

                :already_resumed ->
                  {:close, 3008, "Session already resumed or not yet disconnected"}
              end
            end
        end
    end
  end

  defp op({:ping, message}, state) do
    case validate_message(
           %{
             "type" => "object",
             "properties" => %{
               "op" => %{
                 "type" => "integer"
               },
               "d" => %{
                 "type" => "integer"
               }
             },
             "required" => [
               "d"
             ]
           },
           message
         ) do
      {:error, reason} ->
        Logger.error(inspect(reason))
        {:close, 3005, Jsonrs.encode!(reason)}

      :ok ->
        if Map.get(message, "d") != state.sequence do
          {:close, 3009, "Invalid heartbeat sequence"}
        else
          ref = hb_timer(state.heartbeat_interval)

          {:reply,
           uncode(
             %Derailed.Payload.Base{
               op: 5,
               s: 0,
               d: nil
             },
             Map.get(state, "compressor")
           ), %{state | heartbeat_cycle_finished: true, sequence: 0, heartbeat_ref: ref}}
        end
    end
  end
end
