defmodule Derailed.Brew.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      {GRPC.Server.Supervisor, endpoint: Derailed.GRPC.Endpoint, port: 17000}
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Derailed.Brew.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
