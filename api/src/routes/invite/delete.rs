use actix_web::{delete, web::Path, HttpRequest};
use mineral::{
    acquire,
    auth::{fisr, get_member},
    errors::{CommonError, CommonResult},
    flags::{get_channel_permissions, get_permissions, Permissions},
    Invite,
};

#[delete("/guilds/{guild_id}/channels/{channel_id}/invites/{invite_id}")]
async fn delete_invite(req: HttpRequest, path: Path<(i64, i64, String)>) -> CommonResult<String> {
    let (guild_id, channel_id, invite_id) = path.into_inner();

    let session = acquire().await;
    let user = fisr(req, session).await?;

    let (_, member) = get_member(&guild_id, &user, session).await?;
    let guild_permissions = get_permissions(&guild_id, &member, session).await?;
    let permissions =
        get_channel_permissions(&guild_id, &channel_id, &member, &guild_permissions, session)
            .await?;

    let invite = sqlx::query_as!(Invite, "SELECT * FROM invites WHERE id = $1", &invite_id)
        .fetch_optional(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

    if let Some(inv) = invite {
        if !permissions.contains(Permissions::CREATE_INVITES)
            && inv.author_id.unwrap_or(0) != user.id
        {
            return Err(CommonError::InvalidPermissions);
        }

        sqlx::query!("DELETE FROM invites WHERE id = $1", &inv.id)
            .execute(session)
            .await
            .map_err(|_| CommonError::InternalError)?;

        Ok("".to_owned())
    } else {
        Err(CommonError::InviteDoesNotExist)
    }
}
