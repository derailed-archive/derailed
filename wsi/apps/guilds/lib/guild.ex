defmodule Derailed.Guild do
  @moduledoc """
  GenServer for representing online Derailed guilds.
  """
  require Logger
  use GenServer

  # middle end
  def start_link(guild_id) do
    Logger.debug("Spinning up new Guild: #{inspect(guild_id)}")
    GenServer.start_link(__MODULE__, guild_id)
  end

  def init(guild_id) do
    {:ok,
     %{
       id: guild_id,
       sessions: Map.new()
     }}
  end

  # Session API
  @spec subscribe(pid(), pid(), integer()) :: :ok
  def subscribe(pid, session_pid, user_id) do
    Logger.debug("Subscribing #{inspect(session_pid)} to #{inspect(pid)}")
    GenServer.cast(pid, {:subscribe, session_pid, user_id})
  end

  @spec unsubscribe(pid(), pid()) :: :ok
  def unsubscribe(pid, session_pid) do
    Logger.debug("Unsubscribing #{inspect(session_pid)} to #{inspect(pid)}")
    GenServer.cast(pid, {:unsubscribe, session_pid})
  end

  @spec get_members(pid(), pid()) :: :ok
  def get_members(pid, session_pid) do
    GenServer.cast(pid, {:get_members, session_pid})
  end

  # shared between the gRPC & sessions interfaces
  @spec publish(pid(), any()) :: :ok
  def publish(pid, message) do
    GenServer.call(pid, {:publish, message})
  end

  # backend api
  def handle_cast({:subscribe, pid, user_id}, state) do
    ref = ZenMonitor.monitor(pid)

    {:noreply,
     %{state | sessions: Map.put(state.sessions, pid, %{pid: pid, user_id: user_id, ref: ref})}}
  end

  def handle_cast({:unsubscribe, pid}, state) do
    curmap = Map.get(state.sessions, pid)

    ZenMonitor.demonitor(curmap.ref)

    nmp = Map.delete(state.sessions, pid)

    if nmp == Map.new() do
      GenRegistry.stop(Derailed.Guild, state.id)
    end

    {:noreply, %{state | sessions: nmp}}
  end

  def handle_cast({:get_members, session_pid}, state) do
    stmt =
      Postgrex.prepare!(:db, "get_guild_members", "SELECT * FROM members WHERE guild_id = $1")

    results = Postgrex.execute!(:db, stmt, [state.id])
    maps = Derailed.Utils.maps!(results)

    maps =
      Enum.map(maps, fn map ->
        get_member_roles =
          Postgrex.prepare!(
            :db,
            "get_member_roles",
            "SELECT * FROM roles WHERE id IN (SELECT role_id FROM member_assigned_roles WHERE user_id = $1 AND guild_id = $2);"
          )

        get_user = Postgrex.prepare!(:db, "get_user", "SELECT * FROM users WHERE id = $1")

        roles =
          Derailed.Utils.maps!(Postgrex.execute!(:db, get_member_roles, [map.user_id, state.id]))

        user = Derailed.Utils.map!(Postgrex.execute!(:db, get_user, [map.user_id]))

        Map.put(Map.put(Map.delete(map, "user_id"), "user", user), "roles", roles)
      end)

    Manifold.send(session_pid, {:publish, %{t: "MEMBER_CHUNK", d: maps}})
    {:noreply, state}
  end

  def handle_call({:publish, message}, _from, %{sessions: sessions} = state) do
    Logger.debug("Publishing #{inspect(message)} in #{state.id}")
    Enum.each(sessions, &Manifold.send(&1.pid, {:publish, message}))
    {:reply, :ok, state}
  end

  def handle_info({:DOWN, _ref, :process, session_pid, {:zen_monitor, _reason}}, state) do
    Derailed.Guild.unsubscribe(self(), session_pid)

    {:noreply,
     %{
       state
       | sessions: Map.delete(state.sessions, session_pid)
     }}
  end
end
