import Config

config :derailed, :db,
  name: :db,
  database: "DB_DATABASE",
  username: "DB_USERNAME",
  password: "DB_PASSWORD",
  hostname: "DB_HOSTNAME",
  port: "DB_PORT",
  pool_size: 14
