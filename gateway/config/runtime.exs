import Config
import Dotenvy

source!([".env", System.get_env()])

config :derailed, :db,
  name: :db,
  database: env!("DB_DATABASE", :string!),
  username: env!("DB_USERNAME", :string!),
  password: env!("DB_PASSWORD", :string!),
  hostname: env!("DB_HOSTNAME", :string!),
  port: env!("DB_PORT", :string!),
  pool_size: 14
