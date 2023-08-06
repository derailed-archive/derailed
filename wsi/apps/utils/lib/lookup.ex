defmodule Derailed.Lookup do
  @spec lookup_or_start(binary(), module(), atom(), [any()]) :: {:ok, pid} | {:error, any}
  def lookup_or_start(bucket, mod, index, args) do
    Derailed.Router.route(bucket, GenRegistry, :lookup_or_start, index, [mod, bucket, args])
  end

  @spec lookup(binary(), module(), atom()) :: {:ok, pid} | {:error, :not_found}
  def lookup(bucket, mod, index) do
    Derailed.Router.route(bucket, GenRegistry, :lookup, index, [mod, bucket])
  end
end
