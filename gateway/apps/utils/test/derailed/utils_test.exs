defmodule Derailed.UtilsTest do
  use ExUnit.Case
  doctest Derailed.Utils

  test "greets the world" do
    assert Derailed.Utils.hello() == :world
  end
end
