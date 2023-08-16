use std::env;

use serde::{Serialize, Deserialize};
use time::OffsetDateTime;
use jsonwebtoken::{encode, decode, Validation, Algorithm, DecodingKey, Header, EncodingKey};
use crate::errors::Error;


mod jwt_numeric_date {
    use serde::{self, Deserialize, Deserializer, Serializer};
    use time::OffsetDateTime;

    pub fn serialize<S>(date: &OffsetDateTime, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let timestamp = date.unix_timestamp();
        serializer.serialize_i64(timestamp)
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<OffsetDateTime, D::Error>
    where
        D: Deserializer<'de>,
    {
        OffsetDateTime::from_unix_timestamp(i64::deserialize(deserializer)?)
            .map_err(|_| serde::de::Error::custom("invalid Unix timestamp value"))
    }
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
pub struct Token {
    pub token_id: i64,
    pub user_id: i64,
    pub device_id: Option<String>,

    #[serde(with = "jwt_numeric_date")]
    pub created_at: OffsetDateTime,
    #[serde(with = "jwt_numeric_date")]
    exp: OffsetDateTime,
}


impl Token {
    pub fn from_token(token: String) -> Result<Self, Error> {
        let validation = Validation::new(Algorithm::HS256);
        let token_data = decode::<Token>(&token.to_owned(), &DecodingKey::from_secret(env::var("JWT_SECRET").unwrap().as_bytes()), &validation);

        if let Ok(tok) = token_data {
            Ok(tok.claims)
        } else {
            Err(Error::InvalidToken)
        }
    }

    pub fn new_token(
        token_id: i64,
        user_id: i64,
        device_id: Option<String>,
        created_at: OffsetDateTime
    ) -> Result<String, Error> {
        let model = Self {
            token_id,
            user_id,
            device_id,
            created_at,
            exp: OffsetDateTime::from_unix_timestamp(10000000000).unwrap()
        };
        if let Ok(token) = encode(&Header::default(), &model, &EncodingKey::from_secret(env::var("JWT_SECRET").unwrap().as_bytes())) {
            Ok(token)
        } else {
            Err(Error::JWTError)
        }
    }
}
