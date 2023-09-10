use actix_web::{
    get,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
    User,
};

#[get("/users/{user_id}")]
pub async fn get_user(req: HttpRequest, user_id: Path<i64>) -> CommonResult<Json<User>> {
    let session = acquire().await;

    fisr(req, session).await?;

    let user = sqlx::query_as!(
        User,
        "SELECT * FROM users WHERE id = $1",
        user_id.into_inner()
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    if let Some(usr) = user {
        Ok(Json(usr))
    } else {
        Err(CommonError::UserDoesNotExist)
    }
}
