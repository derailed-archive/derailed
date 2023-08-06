defmodule Derailed.GRPCTest do
  use ExUnit.Case
  doctest Derailed.GRPC

  test "greets the world" do
    assert Derailed.GRPC.hello() == :world
  end
end
