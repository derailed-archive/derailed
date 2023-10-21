defmodule Derailed.Guild.MixProject do
  use Mix.Project

  def project do
    [
      app: :guilds,
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
      mod: {Derailed.Guild.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:zen_monitor, "~> 2.1.0"},
      {:manifold, "~> 1.6.0"},
      {:gen_registry, "~> 1.3.0"},
      {:postgrex, "~> 0.17.2"},
      {:utils, in_umbrella: true}
    ]
  end
end
