defmodule Derailed.WebSocket.Cowboy do
  def get_dispatch do
    :cowboy_router.compile([
      {:_,
       [
         {"/", Derailed.WebSocket, %{}}
       ]}
    ])
  end

  def start_link do
    {:ok, _} =
      :cowboy.start_clear(
        :derailed,
        [{:port, 15000}],
        %{
          env: %{
            dispatch: get_dispatch()
          }
        }
      )
  end
end
