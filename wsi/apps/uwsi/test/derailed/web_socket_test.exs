defmodule Derailed.WebSocketTest do
  use ExUnit.Case
  doctest Derailed.WebSocket

  test "greets the world" do
    assert Derailed.WebSocket.hello() == :world
  end
end
