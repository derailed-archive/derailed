defmodule Derailed.BrewTest do
  use ExUnit.Case
  doctest Derailed.Brew

  test "greets the world" do
    assert Derailed.Brew.hello() == :world
  end
end
