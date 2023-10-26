defmodule Derailed.Brew.MixProject do
  use Mix.Project

  def project do
    [
      app: :brew,
      version: "0.0.0",
      build_path: "../../_build",
      config_path: "../../config/config.exs",
      deps_path: "../../deps",
      lockfile: "../../mix.lock",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger],
      mod: {Derailed.Brew.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:grpc, "~> 0.6"},
      {:google_protos, "~> 0.3"},
      {:protobuf, "~> 0.12"},
      {:jsonrs, "~> 0.3.1"},
      {:sessions, in_umbrella: true},
      {:guilds, in_umbrella: true},
    ]
  end
end
