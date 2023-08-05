# This is a MIG25-generated file used for migrations!
# MIG ID: 2023-1691030343-initial.py. You MAY edit/remove this descriptive section if needed.

from cassandra.cluster import Session


# this is set to mig25 since all keyspaces here shouldn't exist on start.
SCYLLA_KEYSPACE = "mig25"


def scylla(s: Session) -> None:
    s.execute("CREATE TABLE IF NOT EXISTS ")
