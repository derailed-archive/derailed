use actix_web::{
    get,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{acquire, auth::fisr, auth::get_member, errors::CommonResult, Guild};

#[get("/guilds/{guild_id}")]
async fn get_guild(req: HttpRequest, guild_id_path: Path<i64>) -> CommonResult<Json<Guild>> {
    let guild_id = guild_id_path.into_inner();
    let session = acquire().await;

    let user = fisr(req, session).await?;
    let (guild, _) = get_member(&guild_id, &user, session).await?;

    Ok(Json(guild))
}
