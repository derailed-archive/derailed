use base64::{
    alphabet,
    engine::{self, general_purpose},
    Engine as _,
};
use itsdangerous::{default_builder, IntoTimestampSigner, TimestampSigner};

pub static B64: engine::GeneralPurpose =
    engine::GeneralPurpose::new(&alphabet::URL_SAFE, general_purpose::NO_PAD);

#[rustler::nif]
fn get_device_id(token: String) -> Result<i64, rustler::Error> {
    let fragments: Vec<&str> = token.split('.').collect();
    if let Some(device_id_str) = fragments.first() {
        let device_id_enc = B64
            .decode(device_id_str)
            .map_err(|_| rustler::Error::Term(Box::new("invalid token")))?;
        let device_id_dec =
            String::from_utf8(device_id_enc).map_err(|_| rustler::Error::Term(Box::new("invalid token")))?;
        Ok(device_id_dec
            .parse::<i64>()
            .map_err(|_| rustler::Error::Term(Box::new("invalid token")))?)
    } else {
        Err(rustler::Error::Term(Box::new("invalid token")))
    }
}

#[rustler::nif]
fn verify_token(token: String, password: String) -> bool {
    let signer = default_builder(password)
        .build()
        .into_timestamp_signer();

    if !signer.unsign(&token).is_ok() {
        false
    } else {
        true
}
}

rustler::init!("Elixir.Derailed.Token", [get_device_id]);
