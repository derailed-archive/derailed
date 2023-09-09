mod get_current_user;
mod get_user;
mod login;
mod modify_current_user;
mod register;

pub use get_current_user::get_current_user as get_current_user_service;
pub use get_user::get_user as get_user_service;
pub use login::login as login_service;
pub use modify_current_user::modify_current_user as modify_current_user_service;
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
