use actix_web::{get, web::Json, HttpRequest};
use mineral::{acquire, auth::fisr, errors::CommonResult, User};

#[get("/users/@me")]
pub async fn get_current_user(req: HttpRequest) -> CommonResult<Json<User>> {
    let session = acquire().await;

    let user = fisr(req, session).await?;

    Ok(Json(user))
}
