use serde::Serialize;
use utoipa::ToSchema;
use scylla::macros::FromRow;

/// Represents a Derailed user.
#[derive(Serialize, Debug, Clone, ToSchema, FromRow)]
pub struct User {
    /// Unique Identity for this User.
    pub id: i64,
    /// The unique username of this User.
    pub username: String,
    /// The more broad display name of this User.
    /// Can be None.
    pub display_name: Option<String>,
    /// This users avatar hash. Always should be valid from a
    /// CDN prespective, or simply None and set default.
    pub avatar: Option<String>,
    /// This user's hashed password.
    #[serde(skip_serializing)]
    pub password: String,
    /// The unique email of this user.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub email: Option<String>,
    /// This user's public flags
    pub flags: i64,
    /// Whether this user is a bot or not
    pub bot: bool,
    /// Whether this is a systematic user or not
    pub system: bool
}


#[derive(Debug, Clone, FromRow)]
pub struct Device {
    /// This device's snowflake id.
    pub id: i64,
    /// The user who owns this device.
    pub user_id: i64
}
