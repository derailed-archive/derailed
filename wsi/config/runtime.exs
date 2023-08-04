import Config
import Dotenvy
alias ExHashRing.Ring

source!([".env", System.get_env()])

config :derailed, :db,
  name: :db,
  database: env!("DB_DATABASE", :string!),
  username: env!("DB_USERNAME", :string!),
  password: env!("DB_PASSWORD", :string!),
  hostname: env!("DB_HOSTNAME", :string!),
  port: env!("DB_PORT", :string!),
  pool_size: 14

config :joken, env!("JWT_SECRET", :string)

config(:derailed, :guild, env("ERLANG_NODES_GUILDS", :string, to_string(node())))
config(:derailed, :session, env("ERLANG_NODES_SESSIONS", :string, to_string(node())))
config(:derailed, :ws, env("ERLANG_NODES_WS", :string, to_string(node())))
config(:derailed, :presence, env("ERLANG_NODES_PRESENCE", :string, to_string(node())))
