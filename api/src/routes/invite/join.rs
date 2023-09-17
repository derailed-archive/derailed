use actix_web::{
    post,
    web::{Json, Path},
    HttpRequest,
};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
    utils::merge_db_guild,
    Channel, DBGuild, Guild, Invite, Member, Role,
};

use crate::brewery::{get_client, publish_guild, publish_user};

#[post("/invites/{invite_id}")]
async fn join_guild(req: HttpRequest, path: Path<String>) -> CommonResult<Json<Guild>> {
    let invite_id = path.into_inner();
    let session = acquire().await;
    let user = fisr(req, session).await?;

    let invite_opt = sqlx::query_as!(Invite, "SELECT * FROM invites WHERE id = $1", invite_id)
        .fetch_optional(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

    if let Some(invite) = invite_opt {
        let member_opt = sqlx::query!(
            "SELECT user_id FROM guild_members WHERE guild_id = $1 AND user_id = $2",
            &invite.guild_id,
            &user.id
        )
        .fetch_optional(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        if member_opt.is_some() {
            return Err(CommonError::AlreadyAGuildMember);
        }

        let db_guild = sqlx::query_as!(
            DBGuild,
            "SELECT * FROM guilds WHERE id = $1;",
            &invite.guild_id
        )
        .fetch_one(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        let roles = sqlx::query_as!(
            Role,
            "SELECT * FROM roles WHERE guild_id = $1;",
            &invite.guild_id
        )
        .fetch_all(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        let channels = sqlx::query_as!(
            Channel,
            "SELECT * FROM channels WHERE guild_id = $1",
            &invite.guild_id
        )
        .fetch_all(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        let db_features = sqlx::query!(
            "SELECT feature FROM guild_features WHERE id = $1",
            &invite.guild_id
        )
        .fetch_all(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        let mut features = Vec::new();

        for feature in db_features {
            features.push(feature.feature);
        }

        let member = sqlx::query_as!(
            Member,
            "INSERT INTO guild_members (user_id, guild_id, joined_at, deaf, mute, nick) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *;",
            &user.id,
            &invite.guild_id,
            time::OffsetDateTime::now_utc(),
            false,
            false,
            Option::<String>::None
        )
        .fetch_one(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        let mut guild = merge_db_guild(db_guild, Some(features), Some(channels), Some(roles));

        let mut client = get_client().await;

        publish_guild(invite.guild_id, "MEMBER_JOIN", &member, &mut client).await?;

        // avoid giving up ownership before MEMBER_JOIN.
        guild.member = Some(member);

        publish_user(user.id, "GUILD_CREATE", &guild, &mut client).await?;

        Ok(Json(guild))
    } else {
        Err(CommonError::InviteDoesNotExist)
    }
}
