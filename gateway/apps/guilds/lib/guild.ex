defmodule Derailed.Guild do
  use GenServer
  require Logger

  def start_link(id) do
    GenServer.start_link(__MODULE__, id)
  end

  def init(id) do
    {_query, guild_result} =
      Postgrex.prepare_execute!(:db, "get_guild", "SELECT * FROM guilds WHERE id = $1;", [id])

    guild = Derailed.Utilities.map!(guild_result)

    {:ok,
     %{
       id: id,
       sessions: Map.new(),
       guild: guild
     }}
  end

  # client
  def publish(pid, type, message) do
    GenServer.call(pid, {:publish, type, message})
  end

  def subscribe(pid, session_pid) do
    GenServer.cast(pid, {:subscribe, session_pid})
  end

  def unsubscribe(pid, session_pid) do
    GenServer.cast(pid, {:unsubscribe, session_pid})
  end

  # server
  def handle_call({:publish, type, message}, from, %{sessions: sessions} = state) do
    Logger.debug(
      "[guild-#{inspect(state.id)}] Publishing call to Guild [#{inspect(type)}][#{inspect(message)}](#{inspect(from)})"
    )

    Enum.each(sessions, &Manifold.send(&1.pid, %{"t" => type, "d" => message}))

    if type == "GUILD_MODIFY" do
      Logger.debug("[guild-#{inspect(state.id)}] Modifying Guild due to event type")
      {:reply, :ok, %{state | guild: message}}
    else
      {:reply, :ok, state}
    end
  end

  def handle_cast({:subscribe, session_pid}, state) do
    Logger.debug("[guild-#{inspect(state.id)}] Subscription added for #{inspect(session_pid)}")

    ref = ZenMonitor.monitor(session_pid)

    Manifold.send(session_pid, %{"t" => "GUILD_CREATE", "d" => state.guild})

    {:noreply,
     %{state | sessions: Map.put(state.sessions, session_pid, %{pid: session_pid, pid_ref: ref})}}
  end

  def handle_cast({:unsubscribe, session_pid}, state) do
    Logger.debug("[guild-#{inspect(state.id)}] Unsubscribing #{inspect(session_pid)}")

    session = Map.get(state.sessions, session_pid)
    ZenMonitor.demonitor(session.ref)
    sessions = Map.delete(state.sessions, session_pid)

    if Enum.empty?(sessions) do
      GenRegistry.stop(Derailed.Guild, state.id)
    else
      {:noreply, %{state | sessions: sessions}}
    end
  end

  def handle_info({:DOWN, _ref, :process, pid, {:zen_monitor, _reason}}, state) do
    Logger.debug("[guild-#{inspect(state.id)}] Session #{pid} is DOWN, unsubscribing")

    {:noreply,
     %{
       state
       | sessions: MapSet.delete(state.sessions, pid)
     }}
  end
end
