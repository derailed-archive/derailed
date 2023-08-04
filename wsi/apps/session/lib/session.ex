defmodule Derailed.Session do
  @moduledoc """
  Session and state handling for users.
  """

  require Logger
  use GenServer

  def start_link(session_id, user_id, interface_pid, shared_session_pid) do
    Logger.debug("Spinning up new Session: #{inspect(session_id)}:#{inspect(user_id)}")
    GenServer.start_link(__MODULE__, {session_id, user_id, interface_pid, shared_session_pid})
  end

  def init({session_id, user_id, interface_pid, shared_session_pid}) do
    {:ok,
     %{
       # basic metadata
       id: session_id,
       user_id: user_id,
       interface_pid: interface_pid,
       connected: true,

       # user information
       guild_pids: Map.new(),
       guild_pids_reversed: Map.new(),
       guild_presence_pids: MapSet.new(),
       shared_session_pid: shared_session_pid,

       # reference tracking
       ## reference: pid
       guild_pid_references: Map.new(),
       guild_presence_references: Map.new(),
       shared_session_reference: ZenMonitor.monitor(shared_session_pid),
       interface_reference: ZenMonitor.monitor(interface_pid)
     }}
  end

  @spec from_token!(String.t()) :: {:ok, map()} | {:err, :invalid_token | :account_disabled}
  def from_token!(token) do
    case Derailed.Token.verify_and_validate(token) do
      {:ok, claims} ->
        stmt = Postgrex.prepare!(:db, "get_user", "SELECT * FROM users WHERE id = $1;")

        user = Derailed.Utils.map!(Postgrex.execute!(:db, stmt, [Map.get(claims, "user_id")]))
        user = Map.delete(user, "password")

        if user.disabled == true do
          {:err, :account_disabled}
        else
          {:ok, user}
        end

      {:error, _reason} ->
        {:err, :invalid_token}
    end
  end

  def handle_cast({:perform_ready, user}, state) do
    # I: fetch ready data

    get_read_states =
      Postgrex.prepare!(:db, "get_read_states", "SELECT * FROM read_states WHERE user_id = $1;")

    get_settings =
      Postgrex.prepare!(:db, "get_settings", "SELECT * FROM settings WHERE user_id = $1;")

    get_joined_guilds =
      Postgrex.prepare!(
        :db,
        "get_joined_guilds",
        "SELECT * FROM guilds WHERE id IN (SELECT guild_id FROM members WHERE user_id = $1)"
      )

    joined_guilds = Derailed.Utils.maps!(Postgrex.execute!(:db, get_joined_guilds, [user.id]))
    settings = Derailed.Utils.map!(Postgrex.execute!(:db, get_settings, [user.id]))
    read_states = Derailed.Utils.map!(Postgrex.execute!(:db, get_read_states, [user.id]))

    # II: implement READY event

    Manifold.send(
      state.interface_pid,
      {:publish,
       %{
         t: "READY",
         d: %{
           user: user,
           settings: settings,
           read_states: read_states,
           guilds:
             Enum.map(joined_guilds, fn guild -> %{"id" => guild.id, "available" => false} end)
         }
       }}
    )

    # III: lookup/startup guild processes

    guild_pids =
      Enum.map(joined_guilds, fn guild ->
        {:ok, pid} = Derailed.Lookup.lookup_or_start(guild.id, Derailed.Guild, :guild, [guild.id])

        Manifold.send(
          state.interface_pid,
          {:publish, %{t: "GUILD_CREATE", d: Map.put(guild, "available", true)}}
        )

        {guild.id, pid}
      end)

    reversed_guild_pids = Enum.map(guild_pids, fn {guild_id, pid} -> {pid, guild_id} end)

    presence_pids =
      Enum.map(joined_guilds, fn guild ->
        {:ok, pid} =
          Derailed.Lookup.lookup_or_start(guild.id, Derailed.Guild.Presences, :presence, [
            guild.id
          ])

        pid
      end)

    # IV: zen_monitor reference tracking
    guild_references = Enum.map(guild_pids, fn {_, pid} -> ZenMonitor.monitor(pid) end)
    presence_references = Enum.map(presence_pids, fn pid -> ZenMonitor.monitor(pid) end)

    # V: shared session connection
    {:ok, shared_session_pid} =
      GenRegistry.lookup_or_start(Derailed.SharedSession, state.user_id, [state.user_id])

    {
      :noreply,
      %{
        state
        | guild_pids: guild_pids,
          guild_pids_reversed: reversed_guild_pids,
          presence_pids: presence_pids,
          guild_pid_references: guild_references,
          guild_presence_references: presence_references,
          shared_session_pid: shared_session_pid
      }
    }
  end
end
