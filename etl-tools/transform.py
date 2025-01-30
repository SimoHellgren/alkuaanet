from decimal import Decimal
from core import flatten
from random import random


def v1_to_v2(dump: dict):
    # For song, composer and collection
    # 1. move sk to `search_name`, removing the prefix
    # 2. move pk to sk
    # 3. move type to pk
    # 4. add random number field
    for kind in {"song", "collection", "composer"}:
        rows = dump[kind]
        new_rows = [
            {
                **row,
                "pk": row["type"],
                "sk": row["pk"],
                "search_name": row["sk"].removeprefix("name:"),
                "random": Decimal(str(random())),
            }
            for row in rows
        ]
        dump[kind] = new_rows

    # add tones to memberships
    lookup = {song["sk"]: song["tones"] for song in dump["song"]}
    new_memberships = [{**m, "tones": lookup[m["sk"]]} for m in dump["membership"]]
    dump["membership"] = new_memberships

    # remove "type" from all records
    for record in flatten(vals for k, vals in dump.items() if k != "__meta"):
        if "type" in record:
            del record["type"]

    return dump
