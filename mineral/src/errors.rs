use thiserror::Error;

#[derive(Debug, Clone, Copy, Error, PartialEq)]
pub enum CommonError {
    // auth-related errors
    #[error("Invalid user token")]
    InvalidToken,
    #[error("JWT encoding/decoding error")]
    JWTError,

    // connection-related errors
    #[error("Database Connection Error")]
    ConnectionError,

    // API errors
    #[error("Internal server error")]
    InternalError,
    #[error("Invalid authorization")]
    InvalidAuthorization,
    
}
