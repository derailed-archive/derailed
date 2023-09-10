use std::collections::HashMap;

use actix_web::{post, web::Json, HttpRequest};
use mineral::{
    acquire,
    auth::fisr,
    errors::{CommonError, CommonResult},
    make_snowflake, Channel, Guild,
};
use serde::Deserialize;
use serde_valid::Validate;

use crate::routes::CreateChannel;

fn community() -> String {
    "community".to_owned()
}

#[derive(Debug, Deserialize, Validate)]
pub struct CreateGuild {
    #[validate(max_length = 32)]
    #[validate(min_length = 1)]
    name: String,
    #[serde(default)]
    permissions: Option<i64>,
    #[serde(rename = "type")]
    #[serde(default = "community")]
    #[validate(pattern = r"\b(?:community|nsfw)\b")]
    guild_type: String,
    #[serde(default)]
    #[validate(max_items = 500)]
    channels: Option<Option<Vec<CreateChannel>>>,
}

#[post("/guilds")]
pub async fn create_guild(req: HttpRequest, data: Json<CreateGuild>) -> CommonResult<Json<Guild>> {
    let session = acquire().await;

    let user = fisr(req, session).await?;

    let mut tx = session
        .begin()
        .await
        .map_err(|_| CommonError::InternalError)?;

    let json = data.into_inner();
    let guild_id = make_snowflake();

    sqlx::query!(
        r#"INSERT INTO guilds
        (id, name, permissions, type, icon, owner_id)
        VALUES ($1, $2, $3, $4, $5, $6);"#,
        &guild_id,
        &json.name,
        &json.permissions.unwrap_or(0),
        &json.guild_type,
        Option::<String>::None,
        &user.id
    )
    .execute(tx.as_mut())
    .await
    .map_err(|_| CommonError::InternalError)?;

    let mut channels = vec![
        CreateChannel {
            id: Some(0),
            name: "General".to_owned(),
            channel_type: 0,
            position: Some(0),
            topic: None,
            parent_id: None,
            sync_parent_permissions: false,
        },
        CreateChannel {
            id: None,
            name: "general".to_owned(),
            channel_type: 1,
            position: Some(0),
            topic: None,
            parent_id: Some(0),
            sync_parent_permissions: true,
        },
    ];
    let mut parent_ids: HashMap<i64, i64> = HashMap::new();
    parent_ids.insert(0, mineral::make_snowflake());

    if let Some(chs) = json.channels {
        if let Some(channels) = chs {
            let mut parents = vec![];
            let mut latest_positions: HashMap<i64, i32> = HashMap::new();
            let mut latest_parent_position: i32 = 0;

            for channel in channels.iter() {
                if (channel.channel_type == 0) && channel.parent_id.is_some() {
                    return Err(CommonError::CatNoParent);
                }

                if channel.channel_type == 0 {
                    if let Some(channel_id) = channel.id {
                        parents.push(channel_id);
                        latest_positions.insert(channel_id, -1);
                    }
                }
            }

            for channel in channels.clone().iter_mut() {
                if let Some(parent_id) = channel.parent_id {
                    if !parents.contains(&parent_id) {
                        return Err(CommonError::ParentDoesNotExist);
                    }

                    let latpos = latest_positions.get(&parent_id).unwrap();

                    channel.position = Some(latpos + 1);
                    latest_positions.insert(parent_id, latpos + 1);
                } else {
                    latest_parent_position += 1;
                    channel.position = Some(latest_parent_position);
                }
            }
        } else {
            channels = vec![];
        }
    }

    let mut real_chans = vec![];

    for channel in channels.iter() {
        let snowflake_id: i64;
        if channel.channel_type == 0 {
            snowflake_id = *parent_ids.get(&channel.id.unwrap()).unwrap();
        } else {
            snowflake_id = mineral::make_snowflake();
        }

        sqlx::query!(
            r#"INSERT INTO channels (id, name, guild_id, type, position, topic, parent_id, sync_parent_permissions)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8);"#,
            snowflake_id,
            &channel.name,
            &guild_id,
            i32::from(channel.channel_type),
            &channel.position.unwrap(),
            channel.topic,
            channel.parent_id,
            &channel.sync_parent_permissions
        )
        .execute(tx.as_mut())
        .await
        .map_err(|_| CommonError::InternalError)?;

        real_chans.push(Channel {
            id: snowflake_id,
            r#type: channel.channel_type as i32,
            guild_id: Some(guild_id),
            name: Some(channel.clone().name),
            position: Some(channel.position.unwrap()),
            topic: channel.clone().topic,
            parent_id: channel.parent_id,
            last_message_id: None,
            sync_parent_permissions: Some(channel.sync_parent_permissions),
        });
    }

    let guild = Guild {
        id: guild_id,
        name: json.name,
        icon: "".to_owned(),
        owner_id: user.id,
        r#type: json.guild_type,
        max_members: 1000,
        permissions: json.permissions.unwrap_or(0),
        features: Some(vec![]),
        channels: Some(vec![]),
        roles: Some(vec![]),
    };

    Ok(Json(guild))
}
