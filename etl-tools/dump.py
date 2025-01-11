import argparse
from datetime import datetime
import json
from pathlib import Path

from core import Table, JSONEncoder, sorted_groupby


def kind_v1(record: dict) -> str:
    if "type" in record:
        return record["type"]

    pk = record["pk"]

    if pk == "sequence":
        return "sequence"


def kind_v2(record: dict) -> str:
    """returns the kind of the record. Useful for groupby"""
    pk: str = record["pk"]

    # basic case where pk is e.g. song or composer
    if pk in {
        "song",
        "composer",
        "collection",
        "opus",
        "sequence",
    }:
        return pk

    if pk.startswith("collection:") or pk.startswith("composer:"):
        return "membership"


TABLES = {
    "songs": (Table("songs", 1), kind_v1),
    "songs_v2": (Table("songs_v2", 2), kind_v2),
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="py dump.py",
        description="Given a table name, dumps the data. Tables need to be registered in dump.py.",
    )

    parser.add_argument("table_name", choices=TABLES.keys())
    args = parser.parse_args()

    tablename = args.table_name

    if tablename not in TABLES:
        raise ValueError(f"`{tablename}` is not registered.")

    table, kind = TABLES[tablename]

    TARGET_FOLDER = Path(__file__).parent / "dumps"
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE = TARGET_FOLDER / f"{table.name}_{timestamp}.json"

    data = {k: list(v) for k, v in sorted_groupby(table.get_data(), key=kind)}

    for k, records in data.items():
        print(f"Found {len(records):>4} records of kind {k}")

    print(f"Total {sum(map(len, data.values())):>4} records")

    data["__meta"] = {
        "table_name": table.name,
        "table_version": table.version,
    }

    with open(FILE, "w") as f:
        json.dump(data, f, cls=JSONEncoder)
