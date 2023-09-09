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
    #[error("User does not exist")]
    UserDoesNotExist = 3000,
}

#[derive(Debug, Serialize)]
pub struct ErrorResp {
    pub code: i32,
    pub message: Option<String>,
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
            Self::UserDoesNotExist => StatusCode::NOT_FOUND,
        }
    }

    fn error_response(&self) -> actix_web::HttpResponse<actix_web::body::BoxBody> {
        let res = HttpResponse::new(self.status_code());
        let message: Option<String> = None;

        let b = ErrorResp {
            code: *self as i32,
            message,
        };
        res.set_body(BoxBody::new(
            to_vec(&b).expect("Failed to encode error response"),
        ))
    }
}
