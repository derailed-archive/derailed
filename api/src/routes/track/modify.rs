use std::collections::HashMap;

use actix_web::{
    patch,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
    DBTrack, Track, TrackReaction, User,
};
use serde::Deserialize;
use serde_valid::Validate;

#[derive(Debug, Deserialize, Validate)]
struct ModifyTrack {
    #[validate(min_length = 1)]
    #[validate(max_length = 2048)]
    content: String,
}

#[patch("/tracks/{track_id}")]
async fn get_track(
    req: HttpRequest,
    track_id_path: Path<i64>,
    Json(data): Json<ModifyTrack>,
) -> CommonResult<Json<Track>> {
    let session = acquire().await;

    let user = fisr(req, session).await?;
    let track_id = track_id_path.into_inner();

    let db_track_maybe = sqlx::query_as!(
        DBTrack,
        "SELECT * FROM tracks WHERE id = $1 AND author_id = $2;",
        &track_id,
        &user.id
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    if db_track_maybe.is_none() {
        return Err(CommonError::TrackDoesNotExist);
    }

    let db_track = db_track_maybe.unwrap();

    let author = if let Some(user_id) = db_track.author_id {
        Some(
            sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1;", &user_id,)
                .fetch_one(session)
                .await
                .map_err(|_| CommonError::InternalError)?,
        )
    } else {
        None
    };

    let reaction_rows = sqlx::query_as!(
        TrackReaction,
        "SELECT * FROM track_reaction WHERE track_id = $1;",
        &db_track.id
    )
    .fetch_all(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    let mut reactions = HashMap::new();

    for reaction in reaction_rows {
        if reactions.contains_key(&reaction.emoji) {
            let current_count = reactions.get(&reaction.emoji).unwrap();
            reactions.insert(reaction.emoji, current_count + 1).unwrap();
        } else {
            reactions.insert(reaction.emoji, 1).unwrap();
        }
    }

    let mut track = Track {
        id: db_track.id,
        // NOTE: this can/will eventually become expensive.
        // a workaround in the future is preferred.
        author,
        guild: None,
        origin_track_id: db_track.origin_track_id,
        r#type: db_track.r#type,
        content: db_track.content,
        reactions,
    };

    sqlx::query!(
        "UPDATE tracks SET content = $2 WHERE id = $1;",
        &track_id,
        &data.content
    )
    .execute(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    track.content = Some(data.content);

    Ok(Json(track))
}
