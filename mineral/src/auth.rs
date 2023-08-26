use itsdangerous::{default_builder, TimestampSigner, IntoTimestampSigner};
use anyhow::Result;
use crate::errors::CommonError;
use crate::models::{User, Device};
use crate::conn::{acquire, ex};


fn get_device_from_token(token: &String) -> Result<i64> {
    let fragments: Vec<&str> = token.split(".").collect();
    if let Some(device_id_str) = fragments.get(0) {
        let device_id: i64 = device_id_str.parse()?;
        return Ok(device_id)
    } else {
        return Err(CommonError::InvalidToken.into())
    }
}


pub async fn get_user(token: &String) -> Result<User> {
    let device_id = get_device_from_token(&token)?;
    let session = acquire().await;

    let device_res = ex(
        "SELECT * FROM devices WHERE id = ?;",
        session,
        (device_id,)
    ).await?;

    if let Ok(device) = device_res.first_row_typed::<Device>() {
        // if the user doesn't exist, we broke something badly
        let user = ex(
            "SELECT * FROM users WHERE id = ?;",
            session,
            (device.user_id,)
        )
            .await?
            .first_row_typed::<User>()?;

        let signer = default_builder(user.clone().password).build().into_timestamp_signer();

        if let Ok(_) = signer.unsign(token) {
            return Err(CommonError::InvalidToken.into())
        } else {
            return Ok(user)
        }
    } else {
        return Err(CommonError::InvalidAuthorization.into())
    }
}
