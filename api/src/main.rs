use actix_web::{App, HttpServer};
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::EnvFilter;
mod brewery;
mod routes;

pub fn configure_tracing(level: String) {
    let subscriber = tracing_subscriber::fmt::layer().pretty();

    let level = EnvFilter::new(level);

    tracing_subscriber::registry()
        .with(subscriber)
        .with(level)
        .init();
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    configure_tracing("debug".to_owned());

    dotenvy::dotenv().expect("Failed to load .env");

    mineral::acquire().await;

    log::info!("Starting up on http://127.0.0.1:14000");

    HttpServer::new(move || App::new().configure(routes::app))
        .bind("0.0.0.0:14000")?
        .run()
        .await
}
