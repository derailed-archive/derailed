defmodule Derailed.GRPC.Server do
  @moduledoc false
  use GRPC.Server, service: Derailed.GRPC.Service

  @spec publish_guild(Derailed.GRPC.Interchange, GRPC.Server.Stream.t()) ::
          Google.Protobuf.Empty.t()
  def publish_guild(exchange, _stream) do
    guild_id = exchange.id

    data = Jsonrs.decode(exchange.d)

    case GenRegistry.lookup(Derailed.Guild, guild_id) do
      {:ok, pid} -> Derailed.Guild.publish(pid, exchange.t, data)
      {:error, :not_found} -> :ok
    end

    %Google.Protobuf.Empty{}
  end

  @spec publish_user(Derailed.GRPC.Interchange, GRPC.Server.Stream.t()) ::
          Google.Protobuf.Empty.t()
  def publish_user(exchange, _stream) do
    user_id = exchange.id

    data = Jsonrs.decode(exchange.d)

    case GenRegistry.lookup(Derailed.Unify, user_id) do
      {:ok, pid} ->
        Derailed.Unify.publish(pid, exchange.t, data)

      {:error, :not_found} ->
        :ok
    end

    %Google.Protobuf.Empty{}
  end

  @spec multipublish(Derailed.GRPC.BulkInterchange, GRPC.Server.Stream.t()) ::
          Google.Protobuf.Empty.t()
  def multipublish(exchange, _stream) do
    user_ids = exchange.uids

    data = Jsonrs.decode(exchange.d)

    Enum.each(user_ids, fn user_id ->
      case GenRegistry.lookup(Derailed.Unify, user_id) do
        {:ok, pid} -> Derailed.Unify.publish(pid, exchange.t, data)
        {:error, :not_found} -> :ok
      end
    end)

    %Google.Protobuf.Empty{}
  end

  @spec get_activity(Derailed.GRPC.GuildInfo, GRPC.Server.Stream.t()) ::
          Derailed.GRPC.GuildMetadata.t()
  def get_activity(_info, _stream) do
    %Derailed.GRPC.GuildMetadata{
      available: true,
      presences: 0
    }
  end
end
