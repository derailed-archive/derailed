use crate::routes::user::TokenResult;
use actix_web::{post, web::Json};
use mineral::{
    acquire,
    auth::create_token,
    errors::{CommonError, CommonResult},
    flags::UserFlags,
    User,
};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
struct CreateUser {
    /// The username wanted for this user
    username: String,
    /// An email used for authentication
    email: String,
    /// Password for authentication
    password: String,
}

/// PRIVATE ROUTE. Public user creation. Not admin
/// user creation route.
#[post("/register")]
async fn register(data: Json<CreateUser>) -> CommonResult<Json<TokenResult>> {
    let session = acquire().await;

    let mut tx = session
        .begin()
        .await
        .map_err(|_| CommonError::InternalError)?;

    let password = bcrypt::hash(&data.password, 16).map_err(|_| CommonError::InternalError)?;
    let id = mineral::make_snowflake();
    let device_id = mineral::make_snowflake();

    sqlx::query!(
        r#"INSERT INTO users
        (id, username, password, email, bot, system, flags)
        VALUES ($1, $2, $3, $4, $5, $6, $7);"#,
        &id,
        data.username,
        &password,
        data.email,
        false,
        false,
        UserFlags::def().bits()
    )
    .execute(tx.as_mut())
    .await
    .map_err(|err| {
        let er = err.into_database_error().unwrap();

        if er.is_unique_violation() {
            CommonError::UsernameOrPasswordTaken
        } else {
            CommonError::InternalError
        }
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

    Ok(Json(TokenResult {
        user: User {
            id,
            username: data.clone().username,
            display_name: None,
            avatar: None,
            password: password.clone(),
            email: Some(data.clone().email),
            flags: UserFlags::def().bits(),
            bot: false,
            system: false,
        },
        token: create_token(&device_id, password),
    }))
}
