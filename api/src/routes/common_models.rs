use mineral::User;
use serde::{Deserialize, Serialize};
use serde_valid::Validate;

#[derive(Serialize, Debug)]
pub struct TokenResult {
    /// The user object created
    pub user: User,
    /// The token used for authorization.
    pub token: String,
}

#[derive(Deserialize, Debug, Validate, Clone)]
pub struct CreateChannel {
    #[serde(default)]
    pub id: Option<i64>,
    /// The name of this new channel
    #[validate(max_length = 32)]
    #[validate(min_length = 1)]
    pub name: String,
    #[serde(rename = "type")]
    pub channel_type: i8,
    #[serde(default)]
    #[validate(minimum = 0)]
    #[validate(maximum = 500)]
    pub position: Option<i32>,
    #[serde(default)]
    #[validate(max_length = 4096)]
    #[validate(min_length = 1)]
    pub topic: Option<String>,
    #[serde(default)]
    pub parent_id: Option<i64>,
    #[serde(default)]
    pub sync_parent_permissions: bool,
}
