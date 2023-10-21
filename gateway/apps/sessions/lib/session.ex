# TODO: resume functionality
defmodule Derailed.Session do
  use GenServer

  def start_link(id, user_id, guild_ids, ws_pid) do
    GenServer.start_link(__MODULE__, {id, user_id, guild_ids, ws_pid})
  end

  def init({id, user_id, guild_ids, ws_pid}) do
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
       ws_down: false
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

  # server
  def handle_cast(:start, state) do
    {:ok, unify_pid} = GenRegistry.lookup_or_start(Derailed.Unify, state.user_id, [state.user_id])
    Derailed.Unify.subscribe(unify_pid, self())

    guild_pids =
      Enum.map(state.guild_ids, fn guild_id ->
        {:ok, guild_pid} = GenRegistry.lookup_or_start(Derailed.Guild, guild_id)
        {guild_pid, guild_id}
      end)

    {:noreply, %{state | guild_pids: guild_pids}}
  end

  def handle_cast(:unqueue, state) do
    Enum.each(:queue.to_list(state.message_queue), fn message ->
      Manifold.send(state.ws_pid, message)
    end)

    {:noreply, %{state | message_queue: :queue.new(), queued: false}}
  end

  def handle_info(:reset, state) do
    GenRegistry.stop(Derailed.Session, state.id)
  end

  def handle_info({:DOWN, ref, :process, pid, {:zen_monitor, _reason}}, state) do
    if ref == state.ref do
      :erlang.send_after(120_000, self(), :reset)
      {:noreply, %{state | ws_down: true, ws_pid: nil, queued: true}}
    else
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
    if state.queued == true do
      {:noreply, %{state | message_queue: :queue.in(message, state.message_queue)}}
    else
      Manifold.send(state.ws_pid, message)
    end
  end
end
