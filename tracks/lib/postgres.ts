import { Pool } from "pg"
import { parse } from "pg-connection-string"

const uri = parse(process.env.PG_URI!)

export let Postgres: Pool = new Pool({
    host: uri.host!,
    port: new Number(uri.port!).valueOf(),
    user: uri.user!,
    password: uri.password!,
    database: uri.database!,
    ssl: false
})
