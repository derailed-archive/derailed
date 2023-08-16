use std::{sync::OnceLock, env};

use scylla::{Session, SessionBuilder};


pub static SCYLLA: OnceLock<Session> = OnceLock::new();


pub fn acquire() -> &'static Session {
    SCYLLA.get().expect("Database not initialized")
}


pub async fn start_db() {
    let session: Session = SessionBuilder::new()
        .known_node(env::var("SCYLLA_URL").unwrap())
        .build()
        .await.unwrap();

    SCYLLA.set(session).unwrap();
}
