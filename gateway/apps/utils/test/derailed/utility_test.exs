defmodule Derailed.UtilityTest do
  use ExUnit.Case
  doctest Derailed.Utility

  test "greets the world" do
    assert Derailed.Utility.hello() == :world
  end
end
