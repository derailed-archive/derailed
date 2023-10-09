use crate::routes::TokenResult;
use actix_web::{http, post, web::Json};
use mineral::{
    acquire,
    auth::create_token,
    errors::{CommonError, CommonResult},
    flags::UserFlags,
    User,
};
use serde::{Deserialize, Serialize};
use serde_valid::Validate;

#[derive(Serialize, Deserialize, Debug, Clone, Validate)]
struct CreateUser {
    /// The username wanted for this user
    #[validate(min_length = 1)]
    #[validate(max_length = 32)]
    username: String,
    /// Password for authentication
    #[validate(min_length = 1)]
    #[validate(max_length = 32)]
    password: String,
}

/// PRIVATE ROUTE. Public user creation. Not admin
/// user creation route.
#[post("/register")]
async fn register(data: Json<CreateUser>) -> CommonResult<(Json<TokenResult>, http::StatusCode)> {
    let session = acquire().await;

    let mut tx = session
        .begin()
        .await
        .map_err(|_| CommonError::InternalError)?;

    let password = bcrypt::hash(&data.password, 16).map_err(|_| CommonError::InternalError)?;
    let id = mineral::make_snowflake().await;
    let device_id = mineral::make_snowflake().await;

    sqlx::query!(
        r#"INSERT INTO users
        (id, username, password, bot, system, flags)
        VALUES
        ($1, $2, $3, $4, $5, $6);"#,
        &id,
        data.username.to_lowercase(),
        &password,
        false,
        false,
        UserFlags::def().bits()
    )
    .execute(tx.as_mut())
    .await
    .map_err(|err| {
        let er = err.into_database_error();

        if let Some(error) = er {
            if error.is_unique_violation() {
                return CommonError::UsernameTaken;
            }
        }

        CommonError::InternalError
    })?;

    sqlx::query!(
        r#"INSERT INTO devices
        (id, user_id)
        VALUES ($1, $2);"#,
        &device_id,
        &id
    )
    .execute(tx.as_mut())
    .await
    .map_err(|_| CommonError::InternalError)?;

    tx.commit().await.map_err(|_| CommonError::InternalError)?;

    Ok((
        Json(TokenResult {
            user: User {
                id,
                username: data.clone().username,
                display_name: None,
                avatar: None,
                password: password.clone(),
                flags: UserFlags::def().bits(),
                bot: false,
                system: false,
            },
            token: create_token(&device_id, password),
        }),
        http::StatusCode::CREATED,
    ))
}
