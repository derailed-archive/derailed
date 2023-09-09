use actix_web::{services, web};
mod user;

pub fn app(cfg: &mut web::ServiceConfig) {
    let s = services![
        // users
        user::register_service,
        user::login_service,
        user::get_current_user_service,
        user::get_user_service
    ];
    cfg.service(s);
}
