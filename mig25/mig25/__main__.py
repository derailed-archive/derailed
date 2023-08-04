import importlib.machinery
import importlib.util
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Annotated

import tomllib
import typer
from cassandra.cluster import Cluster

mig25 = typer.Typer(name="MIG25")

DEFAULT_MIGCONF = """# MIG25 migration configuration
[environment]
scylla_entrypoint = ["SCYLLA_URL HERE!"]

[conf]
add_year_name = true
"""

DEFAULT_MIGFILE = """
# This is a MIG25-generated file used for migrations!
# MIG ID: {mig_id}. You MAY edit/remove this descriptive section if needed.

from cassandra.cluster import Session


SCYLLA_KEYSPACE = "my_keyspace"


def scylla(s: Session) -> None:
    ...

"""

current_dir = Path(os.curdir)
migrations_dir = current_dir.joinpath("migs25")
migconf = migrations_dir.joinpath("mig25.toml")


@mig25.command("setup", help="Setup MIG25 in this directory.")
def setup() -> None:
    assert not migrations_dir.exists(), "Migrations directory already exists."
    assert not migconf.exists(), "MIG25 config already exists."

    migrations_dir.mkdir(exist_ok=True)
    migconf.touch()
    migconf.write_text(DEFAULT_MIGCONF)


@mig25.command("new", help="Create a new migration")
def new(
    name: Annotated[str, typer.Argument(help="What to name this migration")]
) -> None:
    assert migrations_dir.exists(), "Migrations directory does not exist."
    assert migconf.exists(), "MIG25 config does not exist."

    conf = tomllib.loads(migconf.read_text())

    n = str(int(time())) + "-" + name

    if conf["conf"]["add_year_name"] is True:
        dt = datetime.now(tz=timezone.utc)
        n = str(dt.year) + "-" + n

    n += ".py"

    new_mig = migrations_dir.joinpath(n)
    new_mig.touch()
    new_mig.write_text(DEFAULT_MIGFILE.format(mig_id=n))

    print(f"New migration {n}", file=sys.stdout)


@mig25.command("migrate", help="Update your db to the newest migration")
def migrate() -> None:
    assert migrations_dir.exists(), "Migrations directory does not exist."
    assert migconf.exists(), "MIG25 config does not exist."

    conf = tomllib.loads(migconf.read_text())

    migfiles: list[Path] = []

    for f in migrations_dir.glob("**"):
        if f.name.removesuffix(".py") != f.name:
            migfiles.append(f)

    cluster = Cluster(conf["environment"]["scylla_entrypoint"])
    session = cluster.connect()

    session.execute(
        "CREATE KEYSPACE IF NOT EXISTS mig25 WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 3};"
    )

    # create migration tables
    session.execute(
        "CREATE TABLE IF NOT EXISTS migrations (id text PRIMARY KEY, migrated_on int);"
    )

    # get previously finished migrations
    migscylla = session.execute("SELECT id FROM migrations;")

    migrated_ids = [m.id for m in migscylla]

    i = -1

    current_keyspace = None

    migfiles.sort(key=lambda p: p.name)

    newly_migrated_ids = []

    for migfile in migfiles:
        if migfile.name in migrated_ids:
            continue

        newly_migrated_ids.append(migfile.name)
        i += 1
        spec = importlib.util.spec_from_file_location(
            f"migf{i}", str(migfile.absolute())
        )
        mod = importlib.util.module_from_spec(spec)

        if current_keyspace != mod.SCYLLA_KEYSPACE:
            session.execute(f"USE KEYSPACE {mod.SCYLLA_KEYSPACE}")

        mod.scylla(session)

        t = int(time())

        session.execute(
            "INSERT INTO migrations (id, migrated_on) VALUES ($1, $2);",
            [migfile.name, t],
        )

    if i == -1:
        print("No migrations were applied. All up to date!", file=sys.stdout)
    else:
        print(f"Finished {i+1} migrations.\n\n{newly_migrated_ids}", file=sys.stdout)


if __name__ == "__main__":
    mig25()
