# A unified GenServer to handle incoming messages to user-based endpoints.
defmodule Derailed.Unify do
  use GenServer
  require Logger

  # user functions
  def start_link(user_id) do
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

  @spec publish(pid(), String.t(), any()) :: :ok
  def publish(pid, type, message) do
    GenServer.call(pid, {:publish, type, message})
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
  def handle_call({:publish, type, message}, from, state) do
    Logger.debug(
      "[unify-#{inspect(state.id)}] Publishing call [(#{inspect(type)})-#{inspect(message)}-(#{inspect(from)})]"
    )

    Manifold.send(state.sessions, %{"t" => type, "d" => message})
    {:reply, :ok, state}
  end

  def handle_cast({:subscribe, session_pid}, state) do
    Logger.debug("[unify-#{inspect(state.id)}] Subscribing #{inspect(session_pid)}")

    ref = ZenMonitor.monitor(session_pid)

    {:noreply,
     %{
       state
       | sessions: MapSet.put(state.sessions, session_pid),
         references: Map.put(state.references, session_pid, ref)
     }}
  end

  def handle_cast({:unsubscribe, session_pid}, state) do
    Logger.debug("[unify-#{inspect(state.id)}] Unsubscribing #{inspect(session_pid)}")

    {:noreply,
     %{
       state
       | sessions: MapSet.delete(state.sessions, session_pid),
         references: Map.delete(state.references, session_pid)
     }}
  end

  def handle_info({:DOWN, _ref, :process, pid, {:zen_monitor, _reason}}, state) do
    Logger.debug("[unify-#{inspect(state.id)}] Session #{inspect(pid)} is DOWN")

    if MapSet.delete(state.sessions, pid) == MapSet.new() do
      GenRegistry.stop(Derailed.Unify, state.id)
    end

    {:noreply,
     %{
       state
       | sessions: MapSet.delete(state.sessions, pid),
         references: Map.delete(state.references, pid)
     }}
  end
end
