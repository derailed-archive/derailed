defmodule Derailed.Utilities do
  @spec struct_to_map(struct()) :: map()
  def struct_to_map(struct) do
    m = Map.from_struct(struct)
    Map.delete(m, :__meta__)
  end

  @spec map!(Postgrex.Result) :: map()
  def map!(result) do
    case result do
      %{rows: nil} ->
        Map.new()

      %{rows: []} ->
        Map.new()

      %{rows: [row], columns: columns} ->
        mapify(columns, row)

      _ ->
        raise "Error in mapping database result"
    end
  end

  @spec maps!(Postgrex.Result) :: list()
  def maps!(results) do
    case results do
      %{rows: nil} ->
        Map.new()

      %{rows: []} ->
        []

      %{rows: rows, columns: columns} ->
        Enum.map(rows, fn row -> mapify(columns, row) end)

      _ ->
        raise "Error in mapping database results"
    end
  end

  def mappy(map) do
    Map.new(
      Enum.map(map, fn {k, v} ->
        {k, valuem(v)}
      end)
    )
  end

  defp mapify(columns, row) do
    val =
      columns
      |> Enum.zip(row)
      |> Map.new()

    mappy(val)
  end

  defp valuem(v) do
    cond do
      is_struct(v) ->
        struct_to_map(v)

      is_map(v) ->
        mappy(v)

      is_list(v) ->
        Enum.map(v, fn vv -> valuem(vv) end)

      true ->
        v
    end
  end
end
