use std::{sync::OnceLock, env};

use scylla::{Session, SessionBuilder};
use sqlx::{PgPool, postgres::PgPoolOptions};


pub static SCYLLA: OnceLock<Session> = OnceLock::new();
pub static POSTGRES: OnceLock<PgPool> = OnceLock::new();


pub fn acquire() -> (&'static PgPool, &'static Session) {
    (
        POSTGRES.get().expect("Database not initialized"),
        SCYLLA.get().expect("Database not initialized")
    )
}


pub async fn start_dbs() {
    let session: Session = SessionBuilder::new()
        .known_node(env::var("SCYLLA_URL").unwrap())
        .build()
        .await.unwrap();

    SCYLLA.set(session).unwrap();

    let pool = PgPoolOptions::new()
        .connect(&env::var("PG_URL").unwrap())
        .await.unwrap();

    POSTGRES.set(pool).unwrap();
}
