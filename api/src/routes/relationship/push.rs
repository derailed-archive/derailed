use actix_web::web::{Json, Path};
use actix_web::{put, HttpRequest};
use mineral::acquire;
use mineral::auth::fisr;
use mineral::errors::CommonError;
use mineral::{errors::CommonResult, Relationship};
use serde::Deserialize;
use serde_valid::Validate;

#[derive(Debug, Deserialize, Validate)]
struct PushType {
    r#type: Option<i32>,
}

#[put("/users/{user_id}/relationship")]
async fn push_relationship(
    req: HttpRequest,
    user_id_path: Path<i64>,
    Json(data): Json<PushType>,
) -> CommonResult<Json<Option<Relationship>>> {
    if data.r#type != Some(0)
        && data.r#type != Some(1)
        && data.r#type != Some(2)
        && data.r#type.is_some()
    {
        return Err(CommonError::InvalidRelationshipType);
    }

    let session = acquire().await;

    let user = fisr(req, session).await?;
    let user_id = user_id_path.into_inner();

    let ext = sqlx::query!("SELECT id FROM users WHERE id = $1;", &user_id)
        .fetch_optional(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

    if ext.is_none() {
        return Err(CommonError::UserDoesNotExist);
    }

    let other_relation = sqlx::query!(
        "SELECT * FROM relationships WHERE origin_user_id = $1 AND target_user_id = $2;",
        &user_id,
        &user.id
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    if let Some(other) = other_relation {
        if other.relation == 2 {
            return Err(CommonError::Blocked);
        }
    }

    if data.r#type.is_none() {
        sqlx::query!(
            "DELETE FROM relationships WHERE origin_user_id = $1 AND target_user_id = $2;",
            &user.id,
            &user_id
        )
        .execute(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        return Ok(Json(None));
    }

    let current_relation = sqlx::query!(
        "SELECT relation FROM relationships WHERE origin_user_id = $1 AND target_user_id = $2;",
        &user.id,
        &user_id
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    let mut tx = session
        .begin()
        .await
        .map_err(|_| CommonError::InternalError)?;

    if current_relation.is_some() {
        sqlx::query!(
            "UPDATE relationships SET relation = $3 WHERE origin_user_id = $1 AND target_user_id = $2;",
            &user.id,
            &user_id,
            &data.r#type.unwrap()
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;
    } else {
        sqlx::query!(
            "INSERT INTO relationships (origin_user_id, target_user_id, relation) VALUES ($1, $2, $3);",
            &user.id,
            &user_id,
            &data.r#type.unwrap()
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;
    }

    if data.r#type == Some(2) {
        sqlx::query!(
            "DELETE FROM relationships WHERE EXISTS ( SELECT 1 FROM relationships WHERE origin_user_id = $1 AND target_user_id = $2 );",
            &user_id,
            &user.id
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;
    }

    tx.commit().await.map_err(|_| CommonError::InternalError)?;

    if data.r#type.is_some() {
        return Ok(Json(Some(Relationship {
            origin_user_id: user.id,
            target_user_id: user_id,
            relation: data.r#type.unwrap(),
        })));
    }

    Ok(Json(None))
}
