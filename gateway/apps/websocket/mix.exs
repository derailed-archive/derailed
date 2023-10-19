defmodule Derailed.WebSocket.MixProject do
  use Mix.Project

  def project do
    [
      app: :websocket,
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
      mod: {Derailed.WebSocket.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:cowboy, "~> 2.10"},
      {:jsonrs, "~> 0.3.1"},
      {:ex_json_schema, "~> 0.10.1"},
      {:payloads, in_umbrella: true},
      {:tokenrs, in_umbrella: true},
      {:utils, in_umbrella: true}
    ]
  end
end
