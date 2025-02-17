"""Wrapper module around boto3 to simplify interaction with the db.

Mostly meant to simplify calls by hiding implementation details of the
particular DynamoDB table implementation, while still being relatively thin.
"""

import random as rand
from decimal import Decimal
from enum import StrEnum, auto

import boto3
from boto3.dynamodb.conditions import Key

RESOURCE = boto3.resource("dynamodb")
TABLE = RESOURCE.Table("songs_v2")

SEARCH_INDEX = "search_index"
REVERSE_INDEX = "reverse_index"
RANDOM_INDEX = "random_index"


class Kind(StrEnum):
    song = auto()
    composer = auto()
    collection = auto()


def exists(pk: str, sk: str) -> bool:
    # limit return value to sk to save on bandwith
    item = TABLE.get_item(Key={"pk": pk, "sk": sk}, ProjectionExpression="sk")
    return "Item" in item


def get_item(pk: str, sk: str) -> dict | None:
    """Get an item by the primary key"""
    result = TABLE.get_item(Key={"pk": pk, "sk": sk})

    return result.get("Item")


def batch_get(keys: list[dict]) -> list[dict]:
    batch_keys = {TABLE.table_name: {"Keys": keys}}

    response = RESOURCE.batch_get_item(RequestItems=batch_keys)

    return response["Responses"].get(TABLE.table_name, [])


def batch_write(items: list[dict]) -> list[dict]:
    with TABLE.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    # put_item never returns any data, so we just return the items ¯\_(ツ)_/¯
    return items


def batch_delete(keys: list[dict]) -> list[dict]:
    with TABLE.batch_writer() as batch:
        [batch.delete_item(Key=key) for key in keys]

    # delete_item doesn't return data, so we just return the keys
    return keys


# not super excited about the kwargs here but eh
def get_partition(pk: str, **kwargs) -> list[dict]:
    """Get all items in a partition"""
    result = TABLE.query(KeyConditionExpression=Key("pk").eq(pk), **kwargs)

    return result.get("Items", [])


def memberships(pk: str) -> list[dict]:
    """Essentially the same as list_kind but a different signature"""
    result = TABLE.query(KeyConditionExpression=Key("pk").eq(pk))

    return result.get("Items", [])


def search(kind: Kind, string: str) -> dict | None:
    result = TABLE.query(
        IndexName=SEARCH_INDEX,
        KeyConditionExpression=Key("pk").eq(kind)
        & Key("search_name").begins_with(string),
    )

    return result.get("Items")


def reverse_index(sk: str) -> list[dict]:
    result = TABLE.query(
        IndexName=REVERSE_INDEX,
        KeyConditionExpression=Key("sk").eq(sk),
    )

    return result.get("Items")


def _random(kind: Kind) -> dict | None:
    """Try getting a random record.

    Doesn't necessarily return a record due to the way things are implemented
    in the db.

    For songs the probability of this happening is <1% (ca. 2025-01).
    For composers it is higher, and for collections even higher due to the
    smaller number of records.
    """
    result = TABLE.query(
        KeyConditionExpression=Key("pk").eq(kind)
        & Key("random").gt(Decimal(str(rand.random()))),  # noqa: S311
        Limit=1,
        IndexName="random_index",
    )["Items"]

    return result[0] if result else None


def random(kind: Kind) -> dict:
    """Attempts to find a random record until it does"""
    while not (result := _random(kind)):
        pass

    return get_item(kind, result["sk"])


def put(item: dict) -> dict:
    TABLE.put_item(Item=item)

    return item


def delete(pk: str, sk: str) -> dict:
    deleted = TABLE.delete_item(Key={"pk": pk, "sk": sk}, ReturnValues="ALL_OLD")

    return deleted["Attributes"]


def _peek_sequence(kind: Kind) -> int:
    """Utility for checking what the current_value of this record type's sequence is"""
    result = TABLE.get_item(Key={"pk": "sequence", "sk": f"{kind}_id"})

    return int(result["Item"]["current_value"])


def _get_next_id(kind: Kind) -> int:
    """Increments the sequence value and returns it"""
    response = TABLE.update_item(
        Key={
            "pk": "sequence",
            "sk": f"{kind}_id",
        },
        ReturnValues="ALL_NEW",
        UpdateExpression="SET current_value = current_value + :incr",
        ExpressionAttributeValues={":incr": 1},
    )

    return int(response["Attributes"]["current_value"])
