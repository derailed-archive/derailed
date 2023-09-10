use actix_web::{services, web};
mod common_models;
mod guild;
mod user;
pub use common_models::*;

pub fn app(cfg: &mut web::ServiceConfig) {
    let s = services![
        // users
        user::register_service,
        user::login_service,
        user::get_current_user_service,
        user::get_user_service,
        user::modify_current_user_service,
    ];
    cfg.service(s);
}
