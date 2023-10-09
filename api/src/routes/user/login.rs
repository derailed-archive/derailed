use crate::routes::TokenResult;
use actix_web::{post, web::Json};
use mineral::{
    acquire,
    auth::create_token,
    errors::{CommonError, CommonResult},
    make_snowflake,
    models::{Device, User},
};
use serde::Deserialize;
use serde_valid::Validate;

#[derive(Debug, Deserialize, Clone, Validate)]
struct LoginData {
    #[validate(min_length = 1)]
    #[validate(max_length = 32)]
    pub username: String,
    #[validate(min_length = 1)]
    #[validate(max_length = 32)]
    pub password: String,
}

#[post("/login")]
async fn login(data: Json<LoginData>) -> CommonResult<Json<TokenResult>> {
    let session = acquire().await;

    let user = sqlx::query_as!(
        User,
        "SELECT * FROM users WHERE username = $1",
        &data.username.to_lowercase()
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    if let Some(usr) = user {
        // should this be InternalError instead?
        let valid = bcrypt::verify(&data.password, &usr.password)
            .map_err(|_| CommonError::IncorrectPassword)?;

        if !valid {
            return Err(CommonError::IncorrectPassword);
        }

        let device = Device {
            id: make_snowflake().await,
            user_id: usr.clone().id,
        };

        sqlx::query!(
            "INSERT INTO devices (id, user_id) VALUES ($1, $2);",
            &device.id,
            &device.user_id
        )
        .execute(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        Ok(Json(TokenResult {
            user: usr.clone(),
            token: create_token(&device.id, usr.password),
        }))
    } else {
        Err(CommonError::InvalidUsername)
    }
}
