use actix_web::{services, web};
mod user;

pub fn app(cfg: &mut web::ServiceConfig) {
    let s = services![user::register_service];
    cfg.service(s);
}
