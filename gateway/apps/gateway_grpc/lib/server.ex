defmodule Derailed.GRPC.Server do
  @moduledoc false
  use GRPC.Server, service: Derailed.GRPC.Service

  @spec publish_guild(Derailed.GRPC.Interchange, GRPC.Server.Stream.t()) ::
          Google.Protobuf.Empty.t()
  def publish_guild(exchange, _stream) do
    guild_id = exchange.id

    case GenRegistry.lookup(Derailed.Guild, guild_id) do
      {:ok, pid} -> Manifold.send(pid, %{t: exchange.t, d: Jsonrs.decode!(exchange.d)})
      {:error, :not_found} -> :ok
    end

    %Google.Protobuf.Empty{}
  end

  @spec publish_user(Derailed.GRPC.Interchange, GRPC.Server.Stream.t()) ::
          Google.Protobuf.Empty.t()
  def publish_user(exchange, _stream) do
    user_id = exchange.id

    case GenRegistry.lookup(Derailed.SharedSession, user_id) do
      {:ok, pid} ->
        Manifold.send(pid, {:publish, %{t: exchange.t, d: Jsonrs.decode!(exchange.d)}})

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
      case GenRegistry.lookup(Derailed.SharedSession, user_id) do
        {:ok, pid} -> Manifold.send(pid, {:publish, %{t: exchange.t, d: data}})
        {:error, :not_found} -> :ok
      end
    end)

    %Google.Protobuf.Empty{}
  end

  @spec get_activity(Derailed.GRPC.GuildInfo, GRPC.Server.Stream.t()) ::
          Derailed.GRPC.GuildMetadata.t()
  def get_activity(info, _stream) do
    guild_id = info.id

    activity =
      case GenRegistry.lookup(Derailed.Guild, guild_id) do
        {:ok, _pid} ->
          presences =
            case GenRegistry.lookup(Derailed.Guild.Presence, guild_id) do
              {:ok, pid} -> Derailed.Guild.Presences.count(pid)
              {:error, :not_found} -> 0
            end

          %{available: true, presences: presences}

        {:error, :not_found} ->
          %{available: false, presences: 0}
      end

    %Derailed.GRPC.GuildMetadata{
      available: activity.available,
      presences: activity.presences
    }
  end
end
