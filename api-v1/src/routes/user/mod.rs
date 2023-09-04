mod login;
mod register;

pub use login::login as login_service;
pub use register::register as register_service;

use mineral::User;
use serde::Serialize;

#[derive(Serialize, Debug)]
pub struct TokenResult {
    /// The user object created
    pub user: User,
    /// The token used for authorization.
    pub token: String,
}
