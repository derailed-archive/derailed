use std::sync::OnceLock;
use std::time::SystemTime;

pub static DERAILED_EPOCH: i64 = 1649325271415;
static BUCKET_SIZE: i64 = 1000 * 60 * 60 * 24 * 7;

static SF_INCR: OnceLock<i64> = OnceLock::new();

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

pub fn make_snowflake() -> i64 {
    let mut epoch = curtime();

    epoch = (epoch - DERAILED_EPOCH) << 22;

    epoch |= WORKER_ID << 17;

    epoch |= PROCESS_ID.get_or_init(|| std::process::id() as i64 % 32);

    if let Some(incr) = SF_INCR.get() {
        epoch |= incr % 4096;
        SF_INCR.set(incr + 1).unwrap();
    } else {
        SF_INCR.set(2).unwrap();
        epoch |= 1;
    }
    let incr = SF_INCR.get_or_init(|| 0) + 1;
    epoch |= incr % 4096;
    SF_INCR.set(incr).unwrap();

    epoch
}
