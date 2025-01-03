"""Script for migrating data from original songs-table to songs_v2"""

import boto3
from random import random
from decimal import Decimal
from itertools import chain

flatten = chain.from_iterable

dynamo = boto3.resource("dynamodb")

source_table = dynamo.Table("songs")
destination_table = dynamo.Table("songs_v2")


def transform_basic(item):
    """takes a composer, song or collection and returns a better one
    1. move sk to `search_name`, removing the prefix
    2. move pk to sk
    3. move type to pk
    4. add random number field :D
    """
    new_item = {
        **item,
        "pk": item["type"],
        "sk": item["pk"],
        "search_name": item["sk"].removeprefix("name:"),
        "random": Decimal(str(random())),
    }

    return new_item


def get_data():
    i = 1
    response = source_table.scan()
    yield from response["Items"]
    while key := response.get("LastEvaluatedKey"):
        i += 1
        print("Getting page", i)
        response = source_table.scan(ExclusiveStartKey=key)
        yield from response["Items"]


data = list(get_data())

songs = list(filter(lambda x: x.get("type") == "song", data))
composers = list(filter(lambda x: x.get("type") == "composer", data))
collections = list(filter(lambda x: x.get("type") == "collection", data))

opuses = list(filter(lambda x: x.get("type") == "opus", data))
memberships = list(filter(lambda x: x.get("type") == "membership", data))
sequences = list(filter(lambda x: x.get("pk") == "sequence", data))

all_kinds = [
    list(map(transform_basic, songs)),
    list(map(transform_basic, composers)),
    list(map(transform_basic, collections)),
    opuses,
    memberships,
    sequences,
]

assert sum(map(len, all_kinds)) == len(data)


# remove type fields from all records and upload
for i, record in enumerate(flatten(all_kinds), 1):
    if "type" in record:
        del record["type"]

    destination_table.put_item(Item=record)

    if i % 10 == 0:
        print("Uploaded", i, "items")

print("Uploaded", i, "items in total")
