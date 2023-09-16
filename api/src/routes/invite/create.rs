use actix_web::{
    post,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{
    acquire,
    auth::{fisr, get_member},
    errors::{CommonError, CommonResult},
    flags::{get_channel_permissions, get_permissions, Permissions},
    make_invite_id, Invite,
};

#[post("/guilds/{guild_id}/channels/{channel_id}/invites")]
async fn create_invite(req: HttpRequest, path: Path<(i64, i64)>) -> CommonResult<Json<Invite>> {
    let (guild_id, channel_id) = path.into_inner();

    let session = acquire().await;
    let user = fisr(req, session).await?;

    let (_, member) = get_member(&guild_id, &user, session).await?;
    let guild_permissions = get_permissions(&guild_id, &member, session).await?;
    let permissions =
        get_channel_permissions(&guild_id, &channel_id, &member, &guild_permissions, session)
            .await?;

    if !permissions.contains(Permissions::CREATE_INVITES) {
        return Err(CommonError::InvalidPermissions);
    }

    let invite = sqlx::query_as!(
        Invite,
        "INSERT INTO invites (id, guild_id, channel_id) VALUES ($1, $2, $3) RETURNING *;",
        make_invite_id(),
        &guild_id,
        &channel_id
    )
    .fetch_one(session)
    .await
    .map_err(|err| {
        let er = err.as_database_error();

        if let Some(error) = er {
            if error.is_foreign_key_violation() {
                return CommonError::ChannelDoesNotExist;
            }
            if error.is_unique_violation() {
                return CommonError::InternalError;
            }
        }

        CommonError::InternalError
    })?;

    Ok(Json(invite))
}
