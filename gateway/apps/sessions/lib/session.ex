defmodule Derailed.Session do
  use GenServer

  def start_link(id, user_id, guild_ids) do
    GenServer.start_link(__MODULE__, {id, user_id, guild_ids})
  end

  def init({id, user_id, guild_ids}) do
    {:ok,
     %{
       id: id,
       user_id: user_id,
       guild_ids: guild_ids
     }}
  end

  @spec start(pid()) :: :ok
  def start(pid) do
    GenServer.cast(pid, :start)
  end
end
