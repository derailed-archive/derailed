# TODO: resume functionality
defmodule Derailed.Session do
  use GenServer
  require Logger

  def start_link(id, user_id, guild_ids, ws_pid, token) do
    GenServer.start_link(__MODULE__, {id, user_id, guild_ids, ws_pid, token})
  end

  def init({id, user_id, guild_ids, ws_pid, token}) do
    {:ok,
     %{
       id: id,
       user_id: user_id,
       guild_ids: guild_ids,
       guild_pids: Map.new(),
       queued: true,
       message_queue: :queue.new(),
       ws_pid: ws_pid,
       ws_ref: ZenMonitor.monitor(ws_pid),
       ws_down: false,
       token: token
     }}
  end

  @spec start(pid()) :: :ok
  def start(pid) do
    GenServer.cast(pid, :start)
  end

  @spec unqueue(pid()) :: :ok
  def unqueue(pid) do
    GenServer.cast(pid, :unqueue)
  end

  @spec is_token?(pid(), String.t()) :: boolean()
  def is_token?(pid, token) do
    GenServer.call(pid, {:is_token, token})
  end

  @spec resume(pid()) :: :ok | :already_resumed
  def resume(pid) do
    GenServer.call(pid, :resume)
  end

  # server
  def handle_cast(:start, state) do
    Logger.debug("[sessions-#{inspect(state.id)}] Starting session")

    {:ok, unify_pid} = GenRegistry.lookup_or_start(Derailed.Unify, state.user_id, [state.user_id])
    Derailed.Unify.subscribe(unify_pid, self())

    Logger.debug("[sessions-#{inspect(state.id)}] Successfully connected session to Unify")

    Logger.debug("[sessions-#{inspect(state.id)}] Connecting to Guilds")

    guild_pids =
      Enum.map(state.guild_ids, fn guild_id ->
        Logger.debug("[sessions-#{inspect(state.id)}] Connecting to Guild #{inspect(guild_id)}")

        {:ok, guild_pid} = GenRegistry.lookup_or_start(Derailed.Guild, guild_id)
        {guild_pid, guild_id}
      end)

    {:noreply, %{state | guild_pids: guild_pids}}
  end

  def handle_cast(:unqueue, state) do
    Logger.debug("[sessions-#{inspect(state.id)}] Unqueuing queued up messages")

    Enum.each(:queue.to_list(state.message_queue), fn message ->
      Manifold.send(state.ws_pid, message)
    end)

    {:noreply, %{state | message_queue: :queue.new(), queued: false}}
  end

  def handle_call({:handle_info, token}, _from, state) do
    Logger.debug("[sessions-#{inspect(state.id)}] Validating #{inspect(token)}")

    if token == state.token do
      {:reply, true, state}
    else
      {:reply, false, state}
    end
  end

  def handle_call(:resume, ws_pid, state) do
    Logger.debug(
      "[sessions-#{inspect(state.id)}] Attempting to resume session for ws(pid)-[#{inspect(ws_pid)}]"
    )

    if state.ws_down == true do
      :erlang.send_after(1_000, self(), :unqueue)
      {:reply, :ok, %{state | ws_down: false, ws_pid: ws_pid, ws_ref: ZenMonitor.monitor(ws_pid)}}
    else
      {:reply, :already_resumed, state}
    end
  end

  def handle_info(:reset, state) do
    Logger.debug("[sessions-#{inspect(state.id)}] shutting down (reset)")
    GenRegistry.stop(Derailed.Session, state.id)
  end

  def handle_info(:unqueue, state) do
    Logger.debug("[sessions-#{inspect(state.id)}] Unqueuing queued up messages (timer)")

    Enum.each(:queue.to_list(state.message_queue), fn message ->
      Manifold.send(state.ws_pid, message)
    end)

    {:noreply, %{state | message_queue: :queue.new(), queued: false}}
  end

  def handle_info({:DOWN, ref, :process, pid, {:zen_monitor, _reason}}, state) do
    Logger.debug(
      "[sessions-#{inspect(state.id)}] PID #{inspect(pid)} (ref: [#{inspect(ref)}]) is DOWN"
    )

    if ref == state.ws_ref do
      Logger.debug("[sessions-#{inspect(state.id)}] PID is identified as a WebSocket")
      :erlang.send_after(120_000, self(), :reset)
      {:noreply, %{state | ws_down: true, ws_pid: nil, queued: true}}
    else
      Logger.debug("[sessions-#{inspect(state.id)}] PID is identified as a Guild")
      guild_id = Map.get(state.guild_pids, pid)

      Manifold.send(self(), %{
        "t" => "GUILD_DELETE",
        "d" => %{"id" => guild_id, "available" => false}
      })

      guild_pid = GenRegistry.lookup_or_start(Derailed.Guild, guild_id)

      {:noreply,
       %{state | guild_pids: Map.put(Map.delete(state.guild_pids, pid), guild_pid, guild_id)}}
    end
  end

  def handle_info(message, state) do
    Logger.debug(
      "[sessions-#{inspect(state.id)}] message dispatch invocation [#{inspect(message)}]"
    )

    if state.queued == true do
      {:noreply, %{state | message_queue: :queue.in(message, state.message_queue)}}
    else
      Manifold.send(state.ws_pid, message)
    end
  end
end
