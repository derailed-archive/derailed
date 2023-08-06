defmodule Derailed.Router do
  alias ExHashRing.Ring

  @doc """
  Dispatch the given `mod`, `fun`, `args` request
  to the appropriate node based on the `bucket`.
  """
  @spec route(binary(), module(), atom(), atom(), [any()]) :: term()
  def route(bucket, mod, fun, index, args) do
    ring = table(index)

    {:ok, entry} = Ring.find_node(ring, bucket)

    # If the entry node is the current node
    if String.to_existing_atom(entry) == node() do
      apply(mod, fun, args)
    else
      {Derailed.Tasks, entry}
      |> Task.Supervisor.async(Derailed.Router, :route, [bucket, mod, fun, index, args])
      |> Task.await()
    end
  end

  @doc """
  The routing table. Based on index.
  
  Indexes allowed:
    - :guild
    - :presence
    - :session
    - :ws
  """
  @spec table(atom()) :: Ring
  def table(index) do
    case FastGlobal.get(index) do
      nil ->
        {:ok, ring} = Ring.start_link()
        nodes = String.split(Application.fetch_env!(:derailed, index), ",")
        Ring.add_nodes(ring, nodes)
        Enum.each(nodes, fn elm -> String.to_atom(elm) end)
        FastGlobal.put(index, ring)
        ring

      v ->
        v
    end
  end
end
