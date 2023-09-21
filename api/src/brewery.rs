use brew::tonic::transport::Channel;
use brew::wsi::wsi_client::WsiClient;
use mineral::errors::{CommonError, CommonResult};
use serde::Serialize;
use std::env;
use std::sync::OnceLock;

static CLIENT: OnceLock<WsiClient<Channel>> = OnceLock::new();

pub async fn get_client() -> WsiClient<Channel> {
    if let Some(client) = CLIENT.get() {
        client.clone()
    } else {
        let new_client = WsiClient::connect(env::var("WSI_GRPC").unwrap())
            .await
            .unwrap();
        CLIENT.set(new_client).unwrap();

        return CLIENT.get().unwrap().clone();
    }
}

pub async fn publish_guild(
    guild_id: i64,
    t: &str,
    model: &impl Serialize,
    client: &mut WsiClient<Channel>,
) -> CommonResult<()> {
    if std::env::var("NO_GATEWAY").unwrap_or("true".to_owned()) == "true" {
        return Ok(());
    }

    let request = brew::tonic::Request::new(brew::wsi::Interchange {
        id: guild_id,
        t: t.to_string(),
        d: serde_json::to_string(model).map_err(|_| CommonError::InternalError)?,
    });

    client
        .publish_guild(request)
        .await
        .map_err(|_| CommonError::InternalError)?;

    Ok(())
}

pub async fn publish_user(
    user_id: i64,
    t: &str,
    model: &impl Serialize,
    client: &mut WsiClient<Channel>,
) -> CommonResult<()> {
    if std::env::var("NO_GATEWAY").unwrap_or("true".to_owned()) == "true" {
        return Ok(());
    }

    let request = brew::tonic::Request::new(brew::wsi::Interchange {
        id: user_id,
        t: t.to_string(),
        d: serde_json::to_string(model).map_err(|_| CommonError::InternalError)?,
    });

    client
        .publish_user(request)
        .await
        .map_err(|_| CommonError::InternalError)?;

    Ok(())
}
