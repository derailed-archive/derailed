use crate::brewery::{get_client, publish_guild};
use actix_web::{delete, web::Path, HttpRequest};
use mineral::{
    acquire,
    auth::fisr,
    auth::get_member,
    errors::{CommonError, CommonResult},
};
use serde::Serialize;

#[derive(Serialize)]
struct DeletedGuild {
    guild_id: i64,
    // context: this is used internally in the Gateway and Client
    // to determine whether the Guild went offline, or was actually deleted.
    reason: i8,
}

// TODO/NOTE?: Add password verification
#[delete("/guilds/{guild_id}")]
async fn delete_guild(req: HttpRequest, guild_id_path: Path<i64>) -> CommonResult<&'static str> {
    let guild_id = guild_id_path.into_inner();
    let session = acquire().await;
    let mut client = get_client().await;

    let user = fisr(req, session).await?;
    let (guild, member) = get_member(&guild_id, &user, session).await?;

    if guild.owner_id != member.user_id {
        return Err(CommonError::InvalidPermissions);
    }

    sqlx::query!("DELETE FROM guilds WHERE id = $1;", &guild_id)
        .execute(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

    // This should be fine to fail since the Gateway
    // periodically checks whether Guild are still in
    // the DB every couple of minutes.
    publish_guild(
        guild_id,
        "GUILD_DELETE",
        &DeletedGuild {
            guild_id,
            reason: 0,
        },
        &mut client,
    )
    .await?;

    Ok("")
}
