use bitflags::bitflags;

use crate::{
    errors::{CommonError, CommonResult},
    Member,
};

// For anyone sneaking around here:
// https://docs.rs/bitflags/2.3.3/bitflags/example_generated/struct.Flags.html

bitflags! {
    #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
    pub struct UserFlags: i64 {
        const STAFF = 1 << 0;
        const ADMIN = 1 << 1;
        const VERIFIED = 1 << 2;
        const EARLY_SUPPORTER = 1 << 3;
        const VERIFIED_EMAIL =  1 << 4;
    }
}

impl UserFlags {
    pub fn def() -> Self {
        let mut ret = Self::empty();
        ret.toggle(Self::EARLY_SUPPORTER);
        ret
    }

    pub fn clear(&mut self) {
        *self.0.bits_mut() = 0;
    }
}

bitflags! {
    #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
    pub struct Permissions: i64 {
        const ADMINISTRATOR = 1 << 0;

        // I: management
        const MANAGE_CHANNELS = 1 << 1;
        const MANAGE_ROLES = 1 << 2;
        const MANAGE_INVITES = 1 << 3;
        const MANAGE_CHANNEL_HISTORY = 1 << 4;
        const MANAGE_GUILD = 1 << 5;

        // II: moderation
        const HANDLE_BANS = 1 << 6;
        const HANDLE_KICKS = 1 << 7;

        // III: viewing
        const VIEW_CHANNELS = 1 << 8;
        const VIEW_CHANNEL_HISTORY = 1 << 9;

        // IV: creations
        const CREATE_INVITES = 1 << 10;
        const CREATE_MESSAGES = 1 << 11;
    }
}

#[derive(Debug, Clone, Copy)]
pub struct RoleData {
    pub allow: i64,
    pub deny: i64,
    pub position: i32,
}

pub async fn get_permissions(
    guild_id: &i64,
    member: &Member,
    session: impl Copy + sqlx::PgExecutor<'_>,
) -> CommonResult<Permissions> {
    let mut roles = sqlx::query_as!(
        RoleData,
        r#"SELECT allow, deny, position FROM roles WHERE id IN
        (SELECT role_id FROM member_assigned_roles WHERE user_id = $1 AND guild_id = $2);"#,
        &member.user_id,
        guild_id
    )
    .fetch_all(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    let base_perms = sqlx::query!(
        "SELECT permissions, owner_id FROM guilds WHERE id = $1;",
        &guild_id
    )
    .fetch_one(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    let mut permissions: i64 = base_perms.permissions;

    let mut sorted_roles = Vec::new();

    roles.sort_by(|row1, row2| row1.position.cmp(&row2.position));

    for role in roles.iter() {
        sorted_roles.push((role.allow, role.deny));
    }

    for (allow, deny) in sorted_roles.iter() {
        permissions |= allow;
        permissions &= deny;
    }

    let perms = Permissions::from_bits(permissions).unwrap();

    if perms.contains(Permissions::ADMINISTRATOR) || base_perms.owner_id == member.user_id {
        return Ok(Permissions::all());
    }

    Ok(perms)
}

struct ChannelRoleData {
    id: i64,
    position: i64,
}

pub struct PermissionOverwrite {
    pub id: i64,
    pub channel_id: i64,
    pub r#type: i32,
    pub allow: i64,
    pub deny: i64,
}

// NOTE: `permissions` is role + @everyone permissions. Seen above
pub async fn get_channel_permissions(
    guild_id: &i64,
    channel_id: &i64,
    member: &Member,
    permissions: &Permissions,
    session: impl Copy + sqlx::PgExecutor<'_>,
) -> CommonResult<Permissions> {
    let mut roles = sqlx::query_as!(
        ChannelRoleData,
        r#"SELECT id, position FROM roles WHERE id IN
        (SELECT role_id FROM member_assigned_roles WHERE user_id = $1 AND guild_id = $2);"#,
        &member.user_id,
        guild_id
    )
    .fetch_all(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    roles.push(ChannelRoleData {
        id: *guild_id,
        position: 0,
    });

    roles.sort_by(|role1, role2| role1.position.cmp(&role2.position));

    let overwrites = sqlx::query_as!(
        PermissionOverwrite,
        r#"SELECT * FROM permission_overwrites WHERE channel_id = $1;"#,
        channel_id
    )
    .fetch_all(session)
    .await
    .map_err(|_| CommonError::InternalError)?;

    let mut role_ids = Vec::new();

    for role in roles {
        role_ids.push(role.id);
    }

    let mut perms = permissions.bits();

    for overwrite in overwrites {
        if role_ids.contains(&overwrite.id) || overwrite.id == member.user_id {
            perms |= overwrite.allow;
            perms &= overwrite.deny;
        }
    }

    Ok(Permissions::from_bits(perms).unwrap())
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[repr(i8)]
pub enum ChannelType {
    Category = 0,
    Text = 1,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[repr(i8)]
pub enum Status {
    Invisible = 0,
    Online = 1,
    Idle = 2,
    DND = 3,
}
