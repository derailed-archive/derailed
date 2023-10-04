pub mod auth;
pub mod conn;
pub mod errors;
pub mod flags;
pub mod identity;
pub mod models;
pub mod utils;

// exports
pub use conn::{acquire, DB};
pub use identity::{make_bucket, make_buckets, make_invite_id, make_snowflake};
pub use models::*;
pub use sqlx;

#[cfg(test)]
mod tests {
    use super::make_snowflake;

    #[tokio::test]
    async fn sf_test() {
        let sf = make_snowflake().await;
        assert!(sf > 0);
    }
}
