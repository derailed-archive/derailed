use crate::errors::CommonError;
use crate::models::{Device, User};
use anyhow::Result;
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

fn get_device_from_token(token: &str) -> Result<i64> {
    let fragments: Vec<&str> = token.split('.').collect();
    if let Some(device_id_str) = fragments.first() {
        let device_id_enc = B64.decode(device_id_str)?;
        let device_id_dec = String::from_utf8(device_id_enc)?;
        Ok(device_id_dec.parse::<i64>()?)
    } else {
        Err(CommonError::InvalidToken.into())
    }
}

pub async fn get_user(token: &String, session: impl Copy + sqlx::PgExecutor<'_>) -> Result<User> {
    let device_id = get_device_from_token(token)?;

    let device = sqlx::query_as!(Device, "SELECT * FROM devices WHERE id = $1;", device_id)
        .fetch_one(session)
        .await;

    if let Ok(device) = device {
        // if the user doesn't exist, we broke something badly
        let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1;", device.user_id)
            .fetch_one(session)
            .await?;

        let signer = default_builder(user.clone().password)
            .build()
            .into_timestamp_signer();

        if signer.unsign(token).is_ok() {
            Err(CommonError::InvalidToken.into())
        } else {
            Ok(user)
        }
    } else {
        Err(CommonError::InvalidAuthorization.into())
    }
}
