use brew::tonic::transport::Channel;
use brew::wsi::wsi_client::WsiClient;
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
