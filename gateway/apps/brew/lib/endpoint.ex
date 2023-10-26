defmodule Derailed.GRPC.Endpoint do
  use GRPC.Endpoint

  intercept(GRPC.Server.Interceptors.Logger)
  run(Derailed.GRPC.Server)
end
