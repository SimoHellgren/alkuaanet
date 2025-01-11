from decimal import Decimal
from itertools import groupby
import json
import boto3
import boto3.dynamodb.types


def sorted_groupby(it, key):
    yield from groupby(sorted(it, key=key), key=key)


class JSONEncoder(json.JSONEncoder):
    """For serializing Decimal and boto3:s Binary"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, boto3.dynamodb.types.Binary):
            return obj.value.decode("utf-8")
        return super().default(obj)


# scan ends up being the best option because there isn't an easy way to query
# for all of the membership records in one go
def get_data(table):
    i = 1

    print("Getting page", i)
    response = table.scan()
    yield from response["Items"]
    while key := response.get("LastEvaluatedKey"):
        i += 1
        print("Getting page", i)
        response = table.scan(ExclusiveStartKey=key)
        yield from response["Items"]
