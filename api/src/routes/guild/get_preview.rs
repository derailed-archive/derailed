use crate::brewery::get_client;
use actix_web::{
    get,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{
    acquire,
    auth::fisr,
    auth::get_member,
    errors::{CommonError, CommonResult},
    Guild,
};

#[get("/guilds/{guild_id}")]
async fn get_guild_preview(req: HttpRequest, guild_id_path: Path<i64>) -> CommonResult<Json<Guild>> {
    let guild_id = guild_id_path.into_inner();
    let session = acquire().await;

    let user = fisr(req, session).await?;
    let (mut guild, _) = get_member(&guild_id, &user, session).await?;

    let mut wsi_client = get_client().await;

    let request = brew::tonic::Request::new(brew::wsi::GuildInfo {
        id: guild_id,
    });

    let activity = wsi_client
        .get_activity(request)
        .await
        .map_err(|_| CommonError::InternalError)?;
    let metadata = activity.into_inner();

    (guild.available, guild.approximate_presence_count) =
        (Some(metadata.available), Some(metadata.presences));

    // TODO: make this an actual estimate.
    // This isn't a problem right now, but definitely will be in the future.
    let est = sqlx::query!(
        "SELECT count(*) AS estimate FROM guild_members WHERE guild_id = $1",
        &guild_id,
    )
    .fetch_one(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    guild.approximate_member_count = Some(est.estimate.unwrap_or(0));

    Ok(Json(guild))
}
