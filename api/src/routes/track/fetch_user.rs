use std::collections::HashMap;

use actix_web::{
    get,
    web::{Json, Path, Query},
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
struct FetchTracks {
    #[validate(minimum = 5)]
    #[validate(maximum = 100)]
    tracks: i64,
}

#[get("/users/{user_id}/tracks")]
async fn get_user_tracks(
    req: HttpRequest,
    user_id_path: Path<i64>,
    Query(meta): Query<FetchTracks>,
) -> CommonResult<Json<Vec<Track>>> {
    let session = acquire().await;

    let _user = fisr(req, session).await?;
    let user_id = user_id_path.into_inner();

    let author = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1;", &user_id,)
        .fetch_one(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

    let db_tracks = sqlx::query_as!(
        DBTrack,
        "SELECT * FROM tracks WHERE author_id = $1 ORDER BY id DESC LIMIT $2",
        &user_id,
        &meta.tracks
    )
    .fetch_all(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    let mut tracks: Vec<Track> = Vec::new();

    for db_track in db_tracks {
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

        tracks.push(Track {
            id: db_track.id,
            // NOTE: this can/will eventually become expensive.
            // a workaround in the future is preferred.
            author: Some(author.clone()),
            guild: None,
            origin_track_id: db_track.origin_track_id,
            r#type: db_track.r#type,
            content: db_track.content,
            reactions,
        })
    }

    Ok(Json(tracks))
}
