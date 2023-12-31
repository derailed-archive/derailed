use serde::{Serialize, Deserialize};
use utoipa::ToSchema;

/// Represents a Derailed user.
#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
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
    /// This user's public flags
    pub flags: i64,
    /// Whether this user is a bot or not
    pub bot: bool,
    /// Whether this is a systematic user or not
    pub system: bool,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct GuildSlot {
    /// The Folder witholding this slot.
    pub folder_id: i64,
    /// The guild id of this slot.
    pub guild_id: i64,
    /// The position of this Guild in the folder
    pub position: i32,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Folder {
    /// The id of this folder
    pub id: i64,
    /// The name of this folder.
    /// If None and id == User.id, this is the default folder
    /// otherwise if None, it should be the name of some of the Guilds inside combined.
    pub name: Option<String>,
    /// The user whom this folder belongs to.
    pub user_id: String,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Settings {
    /// The theme this user uses. Either sinful
    /// `light` mode, or glorious `dark` mode.
    pub theme: String,
    /// The latest active status of this User.
    pub status: i8,
    /// The folders owned by this User.
    pub guild_folders: Vec<Folder>,
    /// A list of Guild positions.
    pub guild_slots: Vec<GuildSlot>,
}

/// Represents a device which a user has.
#[derive(Debug, Deserialize, Clone)]
pub struct Device {
    /// This device's snowflake id.
    pub id: i64,
    /// The user who owns this device.
    pub user_id: i64,
}

#[derive(Serialize, Debug, Clone, ToSchema)]
pub struct DBGuild {
    /// The chosen ID of this Guild.
    pub id: i64,
    /// The user-chosen name of this Guild.
    pub name: String,
    /// The
    pub icon: String,
    /// The owner of this Guild.
    pub owner_id: i64,
    /// The type of Guild. One of:
    /// - community
    /// - nsfw
    pub r#type: String,
    /// The maximum number of members this Guild can hold.
    pub max_members: i32,
    /// Default "@everyone" permissions.
    pub permissions: i64,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Guild {
    /// The chosen ID of this Guild.
    pub id: i64,
    /// The user-chosen name of this Guild.
    pub name: String,
    /// The
    pub icon: String,
    /// The owner of this Guild.
    pub owner_id: i64,
    /// The type of Guild. One of:
    /// - community
    /// - nsfw
    pub r#type: String,
    /// The maximum number of members this Guild can hold.
    pub max_members: i32,
    /// Default "@everyone" permissions.
    pub permissions: i64,
    /// This Guild's system specific features.
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub features: Option<Vec<String>>,
    /// The channels of this Guild.
    /// Only sent on endpoints which invoke GUILD_CREATE.
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channels: Option<Vec<Channel>>,
    /// The roles of this Guild.
    /// Only sent on endpoints which invoke GUILD_CREATE.
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub roles: Option<Vec<Role>>,
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub available: Option<bool>,
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub approximate_member_count: Option<i64>,
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub approximate_presence_count: Option<i32>,
    #[serde(default)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub member: Option<Member>,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Member {
    /// Originating User ID of this member
    pub user_id: i64,
    /// Originating Guild ID of this member
    pub guild_id: i64,
    /// The nickname chosen for this member
    pub nick: Option<String>,
    /// When this member joined
    #[serde(with = "time::serde::iso8601")]
    pub joined_at: time::OffsetDateTime,
    /// Whether this member is deafened globally from Voice
    pub deaf: bool,
    /// Whether this member is muted globally from Voice
    pub mute: bool,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Role {
    pub id: i64,
    pub guild_id: i64,
    pub name: String,
    pub allow: i64,
    pub deny: i64,
    pub hoist: bool,
    pub mentionable: bool,
    pub position: i32,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Channel {
    pub id: i64,
    pub r#type: i32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub guild_id: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub position: Option<i32>,
    pub topic: Option<String>,
    pub last_message_id: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_id: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sync_parent_permissions: Option<bool>,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Message {
    pub id: i64,
    pub channel_id: i64,
    pub author_id: Option<i64>,
    pub content: String,
    #[serde(with = "time::serde::iso8601")]
    pub timestamp: time::OffsetDateTime,
    #[serde(with = "time::serde::iso8601::option")]
    pub edited_timestamp: Option<time::OffsetDateTime>,
    pub mention_everyone: bool,
    pub pinned: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(with = "time::serde::iso8601::option")]
    pub pinned_at: Option<sqlx::types::time::OffsetDateTime>,
    pub referenced_message_id: Option<i64>,
    pub flags: i64,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct ReadState {
    pub user_id: i64,
    pub channel_id: i64,
    pub mentions: i64,
    pub last_message_id: Option<i64>,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct PermissionOverwrite {
    pub id: i64,
    pub channel_id: i64,
    pub r#type: i32,
    pub allow: i64,
    pub deny: i64,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct MessageReaction {
    pub message_id: i64,
    pub user_id: i64,
    pub emoji: String,
    #[serde(with = "time::serde::iso8601")]
    pub created_at: time::OffsetDateTime,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Invite {
    pub id: String,
    pub guild_id: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channel_id: Option<i64>,
    pub author_id: Option<i64>,
}

#[derive(Serialize, Deserialize, Debug, Clone, ToSchema)]
pub struct Relationship {
    pub origin_user_id: i64,
    pub target_user_id: i64,
    pub relation: i32
}
