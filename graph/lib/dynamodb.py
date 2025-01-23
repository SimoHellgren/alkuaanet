"""Wrapper module around boto3 to simplify interaction with the db.
Mostly meant to simplify calls by hiding implementation details of the
particular DynamoDB table implementation, while still being relatively thin.
"""

from decimal import Decimal
import random as rand
from enum import StrEnum, auto
import boto3
from boto3.dynamodb.conditions import Key

# TODO: consider managing table name or arn in a configuration file
RESOURCE = boto3.resource("dynamodb")
TABLE = RESOURCE.Table("songs_v2")

SEARCH_INDEX = "search_index"
REVERSE_INDEX = "reverse_index"
RANDOM_INDEX = "random_index"


class Kind(StrEnum):
    song = auto()
    composer = auto()
    collection = auto()


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
        responses = [batch.put_item(Item=item) for item in items]

    # put_item never returns any data, so we just return the items ¯\_(ツ)_/¯
    return items


def batch_delete(keys: list[dict]) -> list[dict]:

    with TABLE.batch_writer() as batch:
        responses = [batch.delete_item(Key=key) for key in keys]

    # delete_item doesn't return data, so we just return the keys
    return keys


def get_partition(pk: str) -> list[dict]:
    """Get all items in a partition"""
    result = TABLE.query(KeyConditionExpression=Key("pk").eq(pk))

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


def _random(kind: Kind) -> dict | None:
    """Try getting a random record. Doesn't necessarily return a record due to
    the way things are implemented in the db.

    For songs the probability of this happening is <1% (ca. 2025-01).
    For composers it is higher, and for collections even higher due to the
    smaller number of records.
    """
    result = TABLE.query(
        KeyConditionExpression=Key("pk").eq(kind)
        & Key("random").gt(Decimal(str(rand.random()))),
        Limit=1,
        IndexName="random_index",
    )["Items"]

    return result[0] if result else None


def random(kind: Kind) -> dict:
    """Attempts to find a random record until it does"""
    i = 1
    while not (result := _random(kind)):
        print("Attempt", i, "at getting random", kind, "unsuccessful.")

    item = get_item(kind, result["sk"])

    return item


def put(item: dict) -> dict:
    response = TABLE.put_item(Item=item)

    # TODO: might want to check for errors here
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

    num = int(response["Attributes"]["current_value"])

    return num
