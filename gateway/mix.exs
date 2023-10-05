defmodule Derailed.Gateway.MixProject do
  use Mix.Project

  def project do
    [
      apps_path: "apps",
      version: "0.0.0",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      releases: [
        # different releases for different strategies:
        # stack: the entirety of the Derailed Gateway
        # grpc: the entirety of the Derailed Gateway's gRPC portion
        # ws: the entirety of the Derailed Gateway's WebSocket portion
        # guild: the Gateway guild portion
        # session: the Gateway session portion
        # presence: the Gateway presence portion

        # grouped
        stack: [
          applications: [
            gateway_grpc: :permanent,
            guilds: :permanent,
            sessions: :permanent,
            cowconn: :permanent,
            presence: :permanent,
            utils: :permanent
          ]
        ],

        # singleton
        grpc: [
          applications: [
            gateway_grpc: :permanent
          ]
        ],
        ws: [
          applications: [
            cowconn: :permanent,
            utils: :permanent
          ]
        ],
        guild: [
          applications: [
            guilds: :permanent,
            utils: :permanent
          ]
        ],
        session: [
          applications: [
            sessions: :permanent,
            utils: :permanent
          ]
        ],
        presences: [
          applications: [
            presence: :permanent,
            utils: :permanent
          ]
        ]
      ]
    ]
  end

  # Dependencies listed here are available only for this
  # project and cannot be accessed from applications inside
  # the apps folder.
  #
  # Run "mix help deps" for examples and options.
  defp deps do
    [
      {:dotenvy, "~> 0.8.0"},
      {:ex_hash_ring, "~> 6.0"},
      {:fastglobal, "~> 1.0"}
    ]
  end
end
