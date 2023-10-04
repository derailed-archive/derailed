use crate::auth::B64;
use base64::Engine as _;
use rand::Rng;
use lazy_static::lazy_static;
use std::time::SystemTime;
use tokio::sync::Mutex;

pub static DERAILED_EPOCH: i64 = 1649325271415;
static BUCKET_SIZE: i64 = 1000 * 60 * 60 * 24 * 7;

lazy_static! {
    static ref SF: Mutex<Snowflake> = Mutex::new(Snowflake::new());
}

// NOTE: these aren't public since these will eventually get replaced once Derailed gets distributed
static DATACENTER_ID: i64 = 1;

fn curtime() -> i64 {
    match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        Ok(n) => n.as_secs() as i64,
        Err(_) => panic!("SystemTime before UNIX EPOCH!"),
    }
}

fn mcurtime() -> i64 {
    match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        Ok(n) => n.as_millis() as i64,
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


#[derive(Debug)]
struct Snowflake {
     sequence: i64
}


impl Snowflake {
    fn new() -> Self {
        Self {
            sequence: 0
        }
    }

    fn get_time(&self) -> i64 {
        mcurtime() - DERAILED_EPOCH
    }

    fn fall(&mut self) -> i64 {
        let timestamp = self.get_time();

        self.sequence = (self.sequence + 1) & (-1 ^ (-1 << 12));

        (timestamp << 22) | (i64::from(std::process::id()) << 17) | (DATACENTER_ID << 12) | self.sequence
    }
}


// TODO: locks bad >:(
pub async fn make_snowflake() -> i64 {
    SF.lock().await.fall()
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
