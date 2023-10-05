defmodule Derailed.SharedSession do
  @moduledoc """
  A shared session discourse for communicating to all sessions of a user.
  """
  require Logger
  use GenServer

  def start_link(user_id) do
    Logger.debug("Spinning up new Session discourse: #{inspect(user_id)}")
    GenServer.start_link(__MODULE__, user_id)
  end

  def init(user_id) do
    {:ok,
     %{
       id: user_id,
       sessions: MapSet.new(),
       references: Map.new()
     }}
  end

  # middle
  @spec publish(pid(), any()) :: term()
  def publish(pid, message) do
    GenServer.call(pid, {:publish, message})
  end

  @spec subscribe(pid(), pid()) :: :ok
  def subscribe(pid, session_pid) do
    GenServer.cast(pid, {:subscribe, session_pid})
  end

  @spec unsubscribe(pid(), pid()) :: :ok
  def unsubscribe(pid, session_pid) do
    GenServer.cast(pid, {:unsubscribe, session_pid})
  end

  # back/core
  def handle_call({:publish, message}, _from, state) do
    Manifold.send(state.sessions, message)
    {:reply, {:ok}, state}
  end

  def handle_cast({:subscribe, session_pid}, state) do
    ref = ZenMonitor.monitor(session_pid)

    {:noreply,
     %{
       state
       | sessions: MapSet.put(state.sessions, session_pid),
         references: Map.put(state.references, session_pid, ref)
     }}
  end

  def handle_cast({:unsubscribe, session_pid}, state) do
    {:noreply,
     %{
       state
       | sessions: MapSet.delete(state.sessions, session_pid),
         references: Map.delete(state.references, session_pid)
     }}
  end

  def handle_info({:DOWN, _ref, :process, pid, {:zen_monitor, _reason}}, state) do
    {:noreply,
     %{
       state
       | sessions: MapSet.delete(state.sessions, pid),
         references: Map.delete(state.references, pid)
     }}
  end
end
