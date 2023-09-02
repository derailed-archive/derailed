use serde::Serialize;
use utoipa::ToSchema;

/// Represents a Derailed user.
#[derive(Serialize, Debug, Clone, ToSchema)]
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
    pub system: bool,
}

#[derive(Serialize, Debug, Clone, ToSchema)]
pub struct DBSettings {
    /// User whom these settings belong to
    user_id: i64,
    /// The theme this user picked.
    /// Either the sinful `light` or gloryful `dark` values.
    theme: String,
    /// This user's latest used status.
    status: i8,
}

#[derive(Serialize, Debug, Clone, ToSchema)]
pub struct GuildSlot {
    /// The Folder witholding this slot.
    folder_id: i64,
    /// The guild id of this slot.
    guild_id: i64,
    /// The position of this Guild in the folder
    position: i32,
}

#[derive(Serialize, Debug, Clone, ToSchema)]
pub struct DBFolder {
    /// The id of this folder
    id: i64,
    /// The name of this folder.
    /// If None and id == User.id, this is the default folder
    /// otherwise if None, it should be the name of some of the Guilds inside combined.
    name: Option<String>,
    /// The user whom this folder belongs to.
    user_id: String,
}

#[derive(Serialize, Debug, Clone, ToSchema)]
pub struct GuildFolder {
    /// The id of this folder
    id: i64,
    /// The name of this folder.
    /// If None and id == User.id, this is the default folder
    /// otherwise if None, it should be the name of some of the Guilds inside combined.
    name: Option<String>,
    /// The user whom this folder belongs to.
    user_id: String,
    /// The slots inside this folder.
    slots: Vec<GuildSlot>,
}

#[derive(Serialize, Debug, Clone, ToSchema)]
pub struct Settings {
    /// The theme this user uses. Either sinful
    /// `light` mode, or glorious `dark` mode.
    theme: String,
    /// The latest active status of this User.
    status: i8,
    /// The folders owned by this User.
    guild_folders: Vec<GuildFolder>,
}

/// Represents a device which a user has.
#[derive(Debug, Clone)]
pub struct Device {
    /// This device's snowflake id.
    pub id: i64,
    /// The user who owns this device.
    pub user_id: i64,
}
