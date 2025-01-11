"""Extract v2 database"""

from datetime import datetime
import json
from pathlib import Path
import boto3
from core import get_data, JSONEncoder, sorted_groupby

TABLE_NAME = "songs_v2"
TABLE_VERSION = 2
RESOURCE = boto3.resource("dynamodb")
TABLE = RESOURCE.Table(TABLE_NAME)
BASIC_KINDS = [
    "song",
    "composer",
    "collection",
    "opus",
    "sequence",
]

KINDS = [*BASIC_KINDS, "membership"]


def kind(record: dict) -> str:
    """returns the kind of the record. Useful for groupby"""

    pk: str = record["pk"]

    # basic case where pk is e.g. song or composer
    if pk in BASIC_KINDS:
        return pk

    if pk.startswith("collection:") or pk.startswith("composer:"):
        return "membership"


if __name__ == "__main__":
    TARGET_FOLDER = Path(__file__).parent / "dumps"
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE = TARGET_FOLDER / f"{TABLE_NAME}_{timestamp}.json"

    data = {k: list(v) for k, v in sorted_groupby(get_data(TABLE), key=kind)}

    for k, records in data.items():
        print(f"Found {len(records):>4} records of kind {k}")

    print(f"Total {sum(map(len, data.values())):>4} records")

    data["__meta"] = {
        "table_name": TABLE_NAME,
        "table_version": 2,
    }

    with open(FILE, "w") as f:
        json.dump(data, f, cls=JSONEncoder)
