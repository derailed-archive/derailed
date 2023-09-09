use actix_web::{patch, web::Json, HttpRequest};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
    User,
};
use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct ModifyUser {
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
    #[serde(default)]
    pub display_name: Option<Option<String>>,
    pub verify_password: String,
}

#[patch("/users/@me")]
pub async fn modify_current_user(
    req: HttpRequest,
    data: Json<ModifyUser>,
) -> CommonResult<Json<User>> {
    let session = acquire().await;

    let mut user = fisr(req, session).await?;

    let mut tx = session
        .begin()
        .await
        .map_err(|_| CommonError::InternalError)?;

    let json = data.into_inner();

    let valid = bcrypt::verify(&json.verify_password, &user.password)
        .map_err(|_| CommonError::InternalError)?;

    if !valid {
        return Err(CommonError::IncorrectPassword);
    }

    if let Some(username) = json.username {
        sqlx::query!(
            "UPDATE users SET username = $1 WHERE id = $2",
            &username,
            user.id
        )
        .execute(tx.as_mut())
        .await
        .map_err(|err| {
            let er = err.into_database_error().unwrap();

            if er.is_unique_violation() {
                CommonError::UsernameTaken
            } else {
                CommonError::InternalError
            }
        })?;

        user.username = username;
    }

    if let Some(password) = json.password {
        let pass = bcrypt::hash(&password, 16).map_err(|_| CommonError::InternalError)?;
        sqlx::query!(
            "UPDATE users SET password = $1 WHERE id = $2",
            &pass,
            user.id
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;

        user.password = pass;
    }

    if let Some(display_name) = json.display_name {
        if let Some(disome) = &display_name {
            sqlx::query!(
                r#"UPDATE users SET display_name = $2 WHERE id = $1"#,
                user.id,
                disome,
            )
            .execute(tx.as_mut())
            .await
            .map_err(|_| CommonError::InternalError)?;
        } else {
            sqlx::query!(
                r#"UPDATE users SET display_name = $2 WHERE id = $1"#,
                user.id,
                Option::<String>::None,
            )
            .execute(tx.as_mut())
            .await
            .map_err(|_| CommonError::InternalError)?;
        }

        user.display_name = display_name;
    }

    tx.commit().await.map_err(|_| CommonError::InternalError)?;

    Ok(Json(user))
}
