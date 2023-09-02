use sqlx::{postgres::PgPoolOptions, PgPool};
use std::{env, sync::OnceLock};

pub static DB: OnceLock<PgPool> = OnceLock::new();

pub async fn acquire() -> &'static PgPool {
    if let Some(db) = DB.get() {
        db
    } else {
        let pool = PgPoolOptions::new()
            .connect(&env::var("PG_URL").unwrap())
            .await
            .unwrap();
        pool.acquire().await.unwrap();
        DB.set(pool).unwrap();
        return DB.get().unwrap();
    }
}
