use actix_cors::Cors;
use actix_web::{App, HttpServer};
use mimalloc::MiMalloc;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::EnvFilter;
mod brewery;
mod routes;

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

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

    HttpServer::new(move || {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_header()
            .allowed_methods(vec!["GET", "POST", "PATCH", "DELETE"])
            .max_age(86400);

        App::new().configure(routes::app).wrap(cors)
    })
    .bind("0.0.0.0:14000")?
    .run()
    .await
}
