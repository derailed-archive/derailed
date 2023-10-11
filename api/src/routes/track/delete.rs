use actix_web::{post, web::Path, HttpRequest};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
};

#[post("/users/@me/tracks/{track_id}")]
async fn delete_track(req: HttpRequest, track_id_path: Path<i64>) -> CommonResult<String> {
    let session = acquire().await;

    let user = fisr(req, session).await?;

    let track_id = track_id_path.into_inner();

    let track = sqlx::query!(
        "SELECT id FROM tracks WHERE id = $1 AND author_id = $2;",
        &track_id,
        &user.id
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    if track.is_some() {
        sqlx::query!(
            "DELETE FROM tracks WHERE id = $1 AND author_id = $2;",
            &track_id,
            &user.id
        )
        .execute(session)
        .await
        .map_err(|_| CommonError::InternalError)?;
    } else {
        return Err(CommonError::TrackDoesNotExist);
    }

    Ok("".to_string())
}
