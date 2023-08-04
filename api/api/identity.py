import os
import threading
import time

__all__ = "snowflake"


BUCKET_SIZE = 1000 * 60 * 60 * 24 * 7
DERAILED_EPOCH = 1649325271415
INCR = 0


def make_snowflake() -> int:
    current_ms = int(time.time() * 1000)

    # timestamp: 63-22
    epoch = current_ms - DERAILED_EPOCH << 22

    # worker id: 21-17
    epoch |= (threading.current_thread().ident % 32) << 17
    # process id: 16-12
    epoch |= (os.getpid() % 32) << 12

    global INCR

    # increment: 11-0
    epoch |= INCR % 4096

    # increment incr to make next snowflake generated, even with the same timestamp
    INCR += 1

    return epoch


def make_bucket(snowflake: int) -> int:
    if snowflake is None:
        timestamp = int(time.time() * 1000) - DERAILED_EPOCH
    else:
        # When a Snowflake is created it contains the number of
        # seconds since the DISCORD_EPOCH.
        timestamp = snowflake >> 22
    return int(timestamp / BUCKET_SIZE)


def make_buckets(start_id: int, end_id: int = None) -> range:
    return range(make_bucket(start_id), make_bucket(end_id) + 1)
