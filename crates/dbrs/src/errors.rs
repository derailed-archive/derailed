pub enum Error {
    // auth-related errors
    InvalidToken,
    JWTError,

    // connection-related errors
    ConnectionError
}
