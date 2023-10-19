defmodule Derailed.Payload.Test do
  use ExUnit.Case
  doctest Derailed.Payload

  test "greets the world" do
    assert Derailed.Payload.hello() == :world
  end
end
