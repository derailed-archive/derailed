use actix_web::{services, web};
mod common_models;
mod guild;
mod invite;
mod relationship;
mod user;
pub use common_models::*;

pub fn app(cfg: &mut web::ServiceConfig) {
    let s_users = services![
        // users
        user::register_service,
        user::login_service,
        user::get_current_user_service,
        user::get_user_service,
        user::modify_current_user_service,
    ];
    let s_relationships = services![relationship::push_relationship,];
    let s_guilds = services![
        guild::create_guild,
        guild::modify_guild,
        guild::delete_guild,
        guild::get_guild,
        guild::get_guild_preview,
    ];
    let s_invites = services![
        invite::create_invite,
        invite::delete_invite,
        invite::join_guild,
    ];

    cfg.service(s_users);
    cfg.service(s_relationships);
    cfg.service(s_guilds);
    cfg.service(s_invites);
}
