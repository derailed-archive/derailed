defmodule Derailed.WebSocket do
  @behaviour :cowboy_websocket
  require Logger

  @spec encode(term(), boolean()) :: binary | iolist()
  defp encode(term, compressor) do
    inp = Jsonrs.encode!(term)

    if compressor != nil do
      :zlib.deflate(compressor, inp, :full)
    else
      inp
    end
  end

  @spec get_op(integer()) :: atom()
  defp get_op(op) do
    %{
      # 0 => :publish,
      1 => :identify,
      # 2 => :resume,
      # 3 => :ack
      4 => :ping
      # 5 => :hello,
    }[op]
  end
end
