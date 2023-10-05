# contains all gRPC-related protobuf models.
defmodule Derailed.GRPC.Interchange do
  use Protobuf, protoc_gen_elixir_version: "1.15.0", syntax: :proto3

  field(:t, 1, type: :string)
  field(:id, 2, type: :int64)
  field(:d, 3, type: Google.Protobuf.Any)
end

defmodule Derailed.GRPC.BulkInterchange do
  use Protobuf, protoc_gen_elixir_version: "1.15.0", syntax: :proto3

  field(:t, 1, type: :string)
  field(:uids, 2, type: :int64, repeated: true)
  field(:d, 3, type: Google.Protobuf.Any)
end

defmodule Derailed.GRPC.GuildInfo do
  use Protobuf, protoc_gen_elixir_version: "1.15.0", syntax: :proto3

  field(:id, 1, type: :int64)
end

defmodule Derailed.GRPC.GuildMetadata do
  use Protobuf, protoc_gen_elixir_version: "1.15.0", syntax: :proto3

  field(:available, 1, type: :bool)
  field(:presences, 2, type: :int32)
end

defmodule Derailed.GRPC.Service do
  use GRPC.Service, name: "derailed.gateway.Gateway", protoc_gen_elixir_version: "0.15.0"

  rpc(:publish_guild, Derailed.GRPC.Interchange, Google.Protobuf.Empty)
  rpc(:publish_user, Derailed.GRPC.Interchange, Google.Protobuf.Empty)
  rpc(:multipublish, Derailed.GRPC.BulkInterchange, Google.Protobuf.Empty)
  rpc(:get_activity, Derailed.GRPC.GuildInfo, Derailed.GRPC.GuildMetadata)
end

defmodule Derailed.GRPC.Stub do
  use GRPC.Stub, service: Derailed.GRPC.Service
end
