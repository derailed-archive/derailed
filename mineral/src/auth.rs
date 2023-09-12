use crate::errors::{CommonError, CommonResult};
use crate::utils::merge_db_guild;
use crate::{DBGuild, Device, Guild, Member, User};
use actix_web::HttpRequest;
use base64::{
    alphabet,
    engine::{self, general_purpose},
    Engine as _,
};
use itsdangerous::{default_builder, IntoTimestampSigner, TimestampSigner};

static B64: engine::GeneralPurpose =
    engine::GeneralPurpose::new(&alphabet::URL_SAFE, general_purpose::NO_PAD);

pub fn create_token(device_id: &i64, password: String) -> String {
    let enc_id = B64.encode(device_id.to_string());

    let signer = default_builder(password).build().into_timestamp_signer();

    signer.sign(enc_id)
}

fn get_device_from_token(token: &str) -> CommonResult<i64> {
    let fragments: Vec<&str> = token.split('.').collect();
    if let Some(device_id_str) = fragments.first() {
        let device_id_enc = B64
            .decode(device_id_str)
            .map_err(|_| CommonError::InternalError)?;
        let device_id_dec =
            String::from_utf8(device_id_enc).map_err(|_| CommonError::InternalError)?;
        Ok(device_id_dec
            .parse::<i64>()
            .map_err(|_| CommonError::InternalError)?)
    } else {
        Err(CommonError::InvalidToken)
    }
}

pub async fn get_user(
    token: String,
    session: impl Copy + sqlx::PgExecutor<'_>,
) -> CommonResult<User> {
    let device_id = get_device_from_token(token.as_str())?;

    let device = sqlx::query_as!(Device, "SELECT * FROM devices WHERE id = $1;", device_id)
        .fetch_one(session)
        .await;

    if let Ok(device) = device {
        // if the user doesn't exist, we broke something badly
        let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1;", device.user_id)
            .fetch_one(session)
            .await
            .map_err(|_| CommonError::InternalError)?;

        let signer = default_builder(user.clone().password)
            .build()
            .into_timestamp_signer();

        if signer.unsign(&token).is_ok() {
            Err(CommonError::InvalidToken)
        } else {
            Ok(user)
        }
    } else {
        Err(CommonError::InvalidAuthorization)
    }
}

pub async fn fisr(
    req: HttpRequest,
    session: impl Copy + sqlx::PgExecutor<'_>,
) -> CommonResult<User> {
    let auth = req.headers().get("authorization");

    if let Some(tok) = auth {
        get_user(
            tok.to_str()
                .map_err(|_| CommonError::InternalError)?
                .to_string(),
            session,
        )
        .await
    } else {
        Err(CommonError::InvalidAuthorization)
    }
}

pub async fn get_member(
    guild_id: &i64,
    user: &User,
    session: impl Copy + sqlx::PgExecutor<'_>,
) -> CommonResult<(Guild, Member)> {
    let member = sqlx::query_as!(
        Member,
        "SELECT * FROM guild_members WHERE user_id = $1 AND guild_id = $2;",
        user.id,
        guild_id
    )
    .fetch_optional(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    if let Some(mem) = member {
        let db_guild =
            sqlx::query_as!(DBGuild, "SELECT * FROM guilds WHERE id = $1;", mem.guild_id)
                .fetch_one(session)
                .await
                .map_err(|_| CommonError::InternalError)?;

        let features_rec = sqlx::query!(
            "SELECT feature FROM guild_features WHERE id = $1;",
            guild_id
        )
        .fetch_all(session)
        .await
        .map_err(|_| CommonError::InternalError)?;

        let mut features = Vec::new();

        for feat in features_rec.iter() {
            features.push(feat.feature.clone());
        }

        let guild = merge_db_guild(db_guild, Some(features), None, None);

        Ok((guild, mem))
    } else {
        Err(CommonError::NotAGuildMember)
    }
}
