defmodule Derailed.WSI.MixProject do
  use Mix.Project

  def project do
    [
      apps_path: "apps",
      version: "0.0.0",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      releases: [
        # different releases for different strategies:
        # stack: the entirety of the Derailed WSI
        # grpc: the entirety of the Derailed WSI's gRPC portion
        # ws: the entirety of the Derailed WSI's WebSocket portion
        # guild: the WSI guild portion
        # session: the WSI session portion
        # presence: the WSI presence portion

        # grouped
        stack: [
          applications: [
            dgrpc: :permanent,
            guilds: :permanent,
            sessions: :permanent,
            uwsi: :permanent,
            presence: :permanent,
            utils: :permanent
          ]
        ],

        # singleton
        grpc: [
          applications: [
            dgrpc: :permanent
          ]
        ],
        ws: [
          applications: [
            uwsi: :permanent,
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
