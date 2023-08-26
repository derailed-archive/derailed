use std::{sync::OnceLock, env};
use scylla::{Session, SessionBuilder, frame::value::ValueList, QueryResult, transport::iterator::RowIterator};
use anyhow::Result;


pub static DB: OnceLock<Session> = OnceLock::new();


pub async fn acquire() -> &'static Session {
    if let Some(db) = DB.get() {
        return db
    } else {
        let session = SessionBuilder::new()
            .known_node(env::var("SCYLLA_URL").unwrap())
            .build()
            .await
            .unwrap();
        DB.set(session).unwrap();
        return DB.get().unwrap()
    }
}


/// A utility function to prepare, and execute a non-paged query.
pub async fn ex(query: &str, db: &Session, values: impl ValueList) -> Result<QueryResult> {
    let prep = db.prepare(query).await?;
    let result = db.execute(&prep, values).await?;
    return Ok(result)
}


/// A utility function to prepare, and execute a non-paged iterable query.
pub async fn exiter(query: &str, db: &Session, values: impl ValueList) -> Result<RowIterator> {
    let prep = db.prepare(query).await?;
    let result = db.execute_iter(prep, values).await?;
    return Ok(result)
}


/// A utility function to prepare, and execute a paged query.
pub async fn page(query: &str, db: &Session, values: impl ValueList) -> Result<QueryResult> {
    let prep = db.prepare(query).await?;
    let result = db.execute_paged(&prep, values, None).await?;
    return Ok(result)
}
