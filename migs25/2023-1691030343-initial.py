# This is a MIG25-generated file used for migrations!
# MIG ID: 2023-1691030343-initial.py. You MAY edit/remove this descriptive section if needed.

from cassandra.cluster import Session


# this is set to mig25 since all keyspaces here shouldn't exist on start.
SCYLLA_KEYSPACE = "mig25"


# TODO: migration for the tables:
# message_reactions
# who_reacted (message_id, reaction, user_id)
# messages
# read_states
# message_channel_mentions (message_id, mentioned_channel_id)
# message_user_mentions (message_id, mentioned_user_id)
# channel_pins (channel_id, bucket_id, message_id) (WHERE: bucket_id is the bucket_id of the message)
# unused_message_buckets (channel_id, bucket_id)
def scylla(s: Session) -> None:
    s.execute("CREATE TABLE IF NOT EXISTS ")
