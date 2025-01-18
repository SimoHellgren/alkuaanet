"""Wrapper module around boto3 to simplify interaction with the db"""

from decimal import Decimal
import random as rand
from enum import StrEnum, auto
import boto3
from boto3.dynamodb.conditions import Key

# TODO: consider managing table name or arn in a configuration file
TABLE = boto3.resource("dynamodb").Table("songs_v2")

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


def list_kind(kind: Kind) -> list[dict]:
    """Get all items of a kind"""
    result = TABLE.query(KeyConditionExpression=Key("pk").eq(kind))

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


def create():
    raise NotImplementedError


def delete():
    raise NotImplementedError


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
