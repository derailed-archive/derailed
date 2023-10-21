defmodule Derailed.Guild do
  use GenServer

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
  def handle_call({:publish, type, message}, _from, %{sessions: sessions} = state) do
    Enum.each(sessions, &Manifold.send(&1.pid, %{"t" => type, "d" => message}))

    if type == "GUILD_MODIFY" do
      {:reply, :ok, %{state | guild: message}}
    else
      {:reply, :ok, state}
    end
  end

  def handle_cast({:subscribe, session_pid}, state) do
    ref = ZenMonitor.monitor(session_pid)

    Manifold.send(session_pid, %{"t" => "GUILD_CREATE", "d" => state.guild})

    {:noreply,
     %{state | sessions: Map.put(state.sessions, session_pid, %{pid: session_pid, pid_ref: ref})}}
  end

  def handle_cast({:unsubscribe, session_pid}, state) do
    session = Map.get(state.sessions, session_pid)
    ZenMonitor.demonitor(session.ref)
    sessions = Map.delete(state.sessions, session_pid)

    if Enum.empty?(sessions) do
      GenRegistry.stop(Derailed.Guild, state.id)
    else
      {:noreply, %{state | sessions: sessions}}
    end
  end
end
