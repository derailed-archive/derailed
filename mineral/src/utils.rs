use crate::{Channel, DBGuild, Guild, Role};

pub fn merge_db_guild(
    db_guild: DBGuild,
    features: Option<Vec<String>>,
    channels: Option<Vec<Channel>>,
    roles: Option<Vec<Role>>,
) -> Guild {
    Guild {
        id: db_guild.id,
        name: db_guild.name,
        icon: db_guild.icon,
        owner_id: db_guild.owner_id,
        r#type: db_guild.r#type,
        max_members: db_guild.max_members,
        permissions: db_guild.permissions,
        features,
        channels,
        roles,
        available: None,
        approximate_member_count: None,
        approximate_presence_count: None
    }
}
