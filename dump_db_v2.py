"""Extract v2 database"""

from datetime import datetime
from decimal import Decimal
from itertools import groupby
import json
from pathlib import Path
import boto3
import boto3.dynamodb.types

RESOURCE = boto3.resource("dynamodb")
TABLE = RESOURCE.Table("songs_v2")
BASIC_KINDS = [
    "song",
    "composer",
    "collection",
    "opus",
    "sequence",
]

KINDS = [*BASIC_KINDS, "membership"]


def sorted_groupby(it, key):
    yield from groupby(sorted(it, key=key), key=key)


def kind(record: dict) -> str:
    """returns the kind of the record. Useful for groupby"""

    pk: str = record["pk"]

    # basic case where pk is e.g. song or composer
    if pk in KINDS:
        return pk

    if pk.startswith("collection:") or pk.startswith("composer:"):
        return "membership"


class Encoder(json.JSONEncoder):
    """For serializing Decimal and boto3:s Binary"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, boto3.dynamodb.types.Binary):
            return obj.value.decode("utf-8")
        return super().default(obj)


# scan ends up being the best option because there isn't an easy way to query
# for all of the membership records in one go
def get_data():
    i = 1

    print("Getting page", i)
    response = TABLE.scan()
    yield from response["Items"]
    while key := response.get("LastEvaluatedKey"):
        i += 1
        print("Getting page", i)
        response = TABLE.scan(ExclusiveStartKey=key)
        yield from response["Items"]


if __name__ == "__main__":
    TARGET_FOLDER = Path("dumps")
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    FILE = TARGET_FOLDER / f"{timestamp}.json"

    data = {k: list(v) for k, v in sorted_groupby(get_data(), key=kind)}

    for k, records in data.items():
        print(f"Found {len(records):>4} records of kind {k}")

    print(f"Total {sum(map(len, data.values())):>4} records")

    with open(FILE, "w") as f:
        json.dump(data, f, cls=Encoder)
