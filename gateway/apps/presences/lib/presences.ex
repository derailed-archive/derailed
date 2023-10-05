defmodule Derailed.Guild.Presences do
  @moduledoc """
  Gateway module responsible for tracking guild presences.
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
       presences: Map.new(),
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

  @spec get_all_presences(pid(), pid()) :: :ok
  def get_all_presences(pid, session_pid) do
    GenServer.cast(pid, {:get_all, session_pid})
  end

  @spec publish_presence(pid(), integer(), map()) :: :ok
  def publish_presence(pid, user_id, presence) do
    GenServer.cast(pid, {:publish, user_id, presence})
  end

  @spec count(pid) :: integer()
  def count(pid) do
    GenServer.call(pid, :count)
  end

  # backend api
  def handle_cast({:subscribe, pid, user_id}, state) do
    ZenMonitor.monitor(pid)
    {:noreply, %{state | sessions: Map.put(state.sessions, pid, %{pid: pid, user_id: user_id})}}
  end

  def handle_cast({:unsubscribe, pid}, state) do
    nmp = Map.delete(state.sessions, pid)
    ZenMonitor.demonitor(pid)

    if nmp == Map.new() do
      GenRegistry.stop(Derailed.Guild.Presences, state.id)
    end

    {:noreply, %{state | sessions: nmp}}
  end

  def handle_cast({:get_all, session_pid}, state) do
    Enum.each(state.presences, &Manifold.send(session_pid, &1))
    {:noreply, state}
  end

  def handle_cast({:publish, user_id, presence}, state) do
    Enum.each(state.sessions, &Manifold.send(&1.pid, Map.put(presence, "guild_id", state.id)))
    {:noreply, %{state | presences: Map.put(state.presences, user_id, presence)}}
  end

  def handle_call(:count, _from, state) do
    {:reply, Enum.count_until(state.presences, 20000), state}
  end

  def handle_info({:DOWN, _ref, :process, session_pid, {:zen_monitor, _reason}}, state) do
    {:noreply,
     %{
       state
       | sessions: Map.delete(state.sessions, session_pid)
     }}
  end
end
