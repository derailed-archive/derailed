use actix_web::{delete, web::Path, HttpRequest};
use mineral::{
    acquire,
    auth::fisr,
    auth::get_member,
    errors::{CommonError, CommonResult},
};

// TODO/NOTE?: Add password verification
#[delete("/guilds/{guild_id}")]
async fn delete_guild(req: HttpRequest, guild_id_path: Path<i64>) -> CommonResult<&'static str> {
    let guild_id = guild_id_path.into_inner();
    let session = acquire().await;

    let user = fisr(req, session).await?;
    let (guild, member) = get_member(&guild_id, &user, session).await?;

    if guild.owner_id != member.user_id {
        return Err(CommonError::InvalidPermissions);
    }

    sqlx::query!("DELETE FROM guilds WHERE id = $1;", guild_id)
        .execute(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

    Ok("")
}
