use crate::auth::B64;
use base64::Engine as _;
use rand::Rng;
use std::sync::OnceLock;
use std::time::SystemTime;

pub static DERAILED_EPOCH: i64 = 1649325271415;
static BUCKET_SIZE: i64 = 1000 * 60 * 60 * 24 * 7;

static SF_GEN: OnceLock<SnowflakeGenerator> = OnceLock::new();

// NOTE: these aren't public since these will eventually get replaced once Derailed gets distributed
static WORKER_ID: i64 = 1;
static PROCESS_ID: OnceLock<i64> = OnceLock::new();

fn curtime() -> i64 {
    match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        Ok(n) => n.as_secs() as i64,
        Err(_) => panic!("SystemTime before UNIX EPOCH!"),
    }
}

pub fn make_bucket(snowflake: i64) -> i64 {
    let timestamp = snowflake >> 22;

    timestamp / BUCKET_SIZE
}

pub fn make_buckets(start_id: i64, end_id: Option<i64>) -> std::ops::Range<i64> {
    make_bucket(start_id)..make_bucket(end_id.unwrap_or(curtime() * 1000))
}

#[derive(Debug, Clone, Copy)]
pub struct SnowflakeGenerator {
    incr: i64
}

impl SnowflakeGenerator {
    pub fn new() -> Self {
        return Self {
            incr: 0
        }
    }

    pub fn generate(mut self) -> i64 {
        self.incr += 1;
        let mut epoch = curtime();

        epoch = epoch - DERAILED_EPOCH << 22;
    
        epoch |= (WORKER_ID % 32) << 17;
    
        epoch |= PROCESS_ID.get_or_init(|| std::process::id() as i64 % 32) << 12;
    
        epoch |= self.incr % 4096;
    
        epoch
    }
}

pub fn make_snowflake() -> i64 {
    let generator = SF_GEN.get_or_init(|| SnowflakeGenerator::new());

    generator.generate()
}

pub fn make_invite_id() -> String {
    let random_bytes: [u8; 16] = rand::thread_rng().gen();
    let base64_encoded = B64.encode(random_bytes);

    // Remove any non-alphanumeric characters and take the first 6 characters
    let invite_id = base64_encoded
        .chars()
        .filter(|c| c.is_ascii_alphanumeric())
        .take(6)
        .collect::<String>();

    invite_id
}
