use actix_web::{
    patch,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{
    acquire,
    auth::fisr,
    auth::get_member,
    errors::{CommonError, CommonResult},
    flags::{get_permissions, Permissions},
    Guild,
};
use serde::Deserialize;
use serde_valid::Validate;

use crate::brewery::{get_client, publish_guild};

#[derive(Debug, Deserialize, Validate)]
pub struct ModifyGuild {
    #[serde(default)]
    #[validate(max_length = 32)]
    #[validate(min_length = 1)]
    name: Option<String>,
    #[serde(default)]
    permissions: Option<i64>,
}

#[patch("/guilds/{guild_id}")]
pub async fn modify_guild(
    req: HttpRequest,
    guild_id_path: Path<i64>,
    data: Json<ModifyGuild>,
) -> CommonResult<Json<Guild>> {
    let guild_id = guild_id_path.into_inner();
    let json = data.into_inner();
    let session = acquire().await;

    let user = fisr(req, session).await?;
    let (mut guild, member) = get_member(&guild_id, &user, session).await?;
    let perms = get_permissions(&guild.id, &member, session).await?;

    if !perms.contains(Permissions::MANAGE_GUILD) {
        return Err(CommonError::InvalidPermissions);
    }

    let mut tx = session
        .begin()
        .await
        .map_err(|_| CommonError::InternalError)?;

    if let Some(permissions) = json.permissions {
        if let Some(new_perms) = Permissions::from_bits(permissions) {
            for perm in new_perms.iter() {
                if !perms.contains(perm) {
                    return Err(CommonError::InvalidPermissions);
                }
            }
        } else {
            return Err(CommonError::InvalidPermissionBitSet);
        }
        sqlx::query!(
            "UPDATE guilds SET permissions = $2 WHERE id = $1",
            &guild.id,
            &permissions
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;

        guild.permissions = permissions;
    }

    if let Some(name) = json.name {
        sqlx::query!(
            "UPDATE guilds SET name = $2 WHERE id = $1",
            &guild.id,
            &name
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;

        guild.name = name;
    }

    let mut client = get_client().await;

    tx.commit().await.map_err(|_| CommonError::InternalError)?;

    publish_guild(guild_id, "GUILD_UPDATE", &guild, &mut client).await?;

    Ok(Json(guild))
}
