use serde::Serialize;
use serde_json::to_vec;
use thiserror::Error;

#[derive(Debug, Clone, Copy, Error, PartialEq)]
#[repr(i32)]
pub enum CommonError {
    #[error("Internal server error")]
    InternalError = 1000,
    #[error("Database Connection Error")]
    ConnectionError = 1001,
    #[error("Invalid authorization")]
    InvalidAuthorization = 2000,
    #[error("Invalid user token")]
    InvalidToken = 2001,
    #[error("Username already taken")]
    UsernameTaken = 2002,
    #[error("Invalid username")]
    InvalidUsername = 2003,
    #[error("Incorrect password")]
    IncorrectPassword = 2004,
    #[error("Invalid permission")]
    InvalidPermissions = 2005,
    #[error("You have been blocked by this User")]
    Blocked = 2006,
    #[error("User does not exist")]
    UserDoesNotExist = 3000,
    #[error("Channel does not exist")]
    ChannelDoesNotExist = 3001,
    #[error("Invite does not exist")]
    InviteDoesNotExist = 3002,
    // 4000, 5000, and 6000 are all reserved
    // for "bad data" errors.
    #[error("Invalid channel position")]
    InvalidChannelPosition = 4000,
    #[error("A category channel cannot have a parent")]
    CatNoParent = 4001,
    #[error("Channel parent does not exist")]
    ParentDoesNotExist = 4002,
    #[error("Invalid permission bit set")]
    InvalidPermissionBitSet = 4003,
    #[error("Not a member of this guild")]
    NotAGuildMember = 4004,
    #[error("Already a member of this guild")]
    AlreadyAGuildMember = 4005,
    #[error("Invalid relationship type")]
    InvalidRelationshipType = 4006,
}

#[derive(Debug, Serialize)]
pub struct ErrorResp {
    pub code: i32,
    pub message: String,
}

pub type CommonResult<T> = Result<T, CommonError>;

use actix_web::{body::BoxBody, http::StatusCode, HttpResponse, ResponseError};

impl ResponseError for CommonError {
    fn status_code(&self) -> StatusCode {
        match self {
            Self::ConnectionError => StatusCode::INTERNAL_SERVER_ERROR,
            Self::InternalError => StatusCode::INTERNAL_SERVER_ERROR,
            Self::InvalidAuthorization => StatusCode::UNAUTHORIZED,
            Self::InvalidToken => StatusCode::UNAUTHORIZED,
            Self::UsernameTaken => StatusCode::BAD_REQUEST,
            Self::InvalidUsername => StatusCode::BAD_REQUEST,
            Self::IncorrectPassword => StatusCode::BAD_REQUEST,
            Self::InvalidPermissions => StatusCode::FORBIDDEN,
            Self::Blocked => StatusCode::FORBIDDEN,
            Self::UserDoesNotExist => StatusCode::NOT_FOUND,
            Self::ChannelDoesNotExist => StatusCode::NOT_FOUND,
            Self::InviteDoesNotExist => StatusCode::NOT_FOUND,
            Self::InvalidChannelPosition => StatusCode::BAD_REQUEST,
            Self::CatNoParent => StatusCode::BAD_REQUEST,
            Self::ParentDoesNotExist => StatusCode::BAD_REQUEST,
            Self::InvalidPermissionBitSet => StatusCode::BAD_GATEWAY,
            Self::NotAGuildMember => StatusCode::FORBIDDEN,
            Self::AlreadyAGuildMember => StatusCode::BAD_REQUEST,
            Self::InvalidRelationshipType => StatusCode::BAD_REQUEST
        }
    }

    fn error_response(&self) -> actix_web::HttpResponse<actix_web::body::BoxBody> {
        let res = HttpResponse::new(self.status_code());
        let message: String = Self::to_string(self);

        let b = ErrorResp {
            code: *self as i32,
            message,
        };
        res.set_body(BoxBody::new(
            to_vec(&b).expect("Failed to encode error response"),
        ))
    }
}
