from decimal import Decimal
from itertools import tee
from random import random
from typing import Callable
from core import Dump, compose, flatten, sorted_groupby


def kindify(dump: Dump, kindfunc: Callable[[dict], str]) -> dict[str, list]:
    """group dump records by their kind, as defined by kindfunc"""
    return {k: list(v) for k, v in sorted_groupby(dump, key=kindfunc)}


def unkindify(data: dict[str, list]) -> Dump:
    """Reverse operation to kindify; return just the values of a kindified dump"""
    yield from flatten(data.values())


def dump_version(dump: Dump) -> int:
    record = next(
        filter(lambda x: x["pk"] == "metadata" and x["sk"] == "table_version", dump)
    )
    return int(record["value"])


def kind_v1(record: dict) -> str:
    """Identifies the kind of record for table_version 1"""
    if "type" in record:
        return record["type"]

    pk = record["pk"]

    if pk == "sequence":
        return "sequence"

    if pk == "metadata":
        return "metadata"


def kind_v2(record: dict) -> str:
    """Identifies the kind of record for table_version 2"""
    pk: str = record["pk"]

    # basic case where pk is e.g. song or composer
    if pk in {
        "song",
        "composer",
        "collection",
        "opus",
        "sequence",
        "metadata",
    }:
        return pk

    if pk.startswith("collection:") or pk.startswith("composer:"):
        return "membership"


def v1_to_v2(dump: Dump) -> Dump:
    """Transform v1 dump to v2 dump"""
    # kindify to handle stuff easier
    dump_ = kindify(dump, kind_v1)

    # For song, composer and collection
    # 1. move sk to `search_name`, removing the prefix
    # 2. move pk to sk
    # 3. move type to pk
    # 4. add random number field
    for kind in {"song", "collection", "composer"}:
        rows = dump_[kind]
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
        dump_[kind] = new_rows

    # add tones to memberships
    lookup = {song["sk"]: song["tones"] for song in dump_["song"]}
    new_memberships = [{**m, "tones": lookup[m["sk"]]} for m in dump_["membership"]]
    dump_["membership"] = new_memberships

    # remove "type" from all records
    for record in flatten(vals for k, vals in dump_.items() if k != "__meta"):
        if "type" in record:
            del record["type"]

    # update metadata record(s)
    dump_["metadata"] = [
        r if r["sk"] != "table_version" else {**r, "table_version": 2}
        for r in dump_["metadata"]
    ]

    yield from unkindify(dump_)


UPGRADERS = {
    1: v1_to_v2,
}


def upgrade(dump: Dump, to_version: int):
    # tee dump to ensure that the whole iterator is not consumed
    dump_a, dump_b = tee(dump)
    from_version = dump_version(dump_a)

    # get and compose required tranformations
    upgrades = [UPGRADERS.get(i) for i in range(from_version, to_version)]
    migrate = compose(*upgrades)

    new_data: Dump = migrate(dump_b)

    return new_data
