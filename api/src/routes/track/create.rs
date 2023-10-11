use std::collections::HashMap;

use actix_web::{post, web::Json, HttpRequest};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
    make_snowflake, Track,
};
use serde::Deserialize;
use serde_valid::Validate;

#[derive(Debug, Deserialize, Validate)]
struct CreateTrack {
    #[validate(min_length = 1)]
    #[validate(max_length = 2048)]
    content: String,
}

#[post("/users/@me/tracks")]
async fn create_track(
    req: HttpRequest,
    Json(data): Json<CreateTrack>,
) -> CommonResult<Json<Track>> {
    let session = acquire().await;

    let user = fisr(req, session).await?;

    let t = sqlx::query!(
        "INSERT INTO tracks (id, author_id, type, content) VALUES ($1, $2, $3, $4) RETURNING id;",
        make_snowflake().await,
        &user.id,
        0,
        &data.content
    )
    .fetch_one(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    Ok(Json(Track {
        id: t.id,
        author: Some(user),
        guild: None,
        origin_track_id: None,
        r#type: 0,
        content: Some(data.content),
        reactions: HashMap::new(),
    }))
}
