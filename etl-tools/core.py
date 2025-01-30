from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property, reduce
from itertools import chain, groupby
import json
import boto3
import boto3.dynamodb.types


class Table:
    def __init__(self, name: str, version: int):
        self.name = name
        self.version = version

    @cached_property
    def resource(self):
        return boto3.resource("dynamodb")

    @cached_property
    def table(self):
        return self.resource.Table(self.name)

    # scan ends up being the best option because there isn't an easy way to query
    # for all of the membership records in one go
    def get_data(self):
        i = 1

        print("Getting page", i)
        response = self.table.scan()
        yield from response["Items"]
        while key := response.get("LastEvaluatedKey"):
            i += 1
            print("Getting page", i)
            response = self.table.scan(ExclusiveStartKey=key)
            yield from response["Items"]

    def populate(self, data: list[dict]):
        with self.table.batch_writer() as batch:
            for item in data:
                batch.put_item(Item=item)


@dataclass
class T2:
    name: str

    @cached_property
    def version(self) -> int:
        result = self.table.get_item(Key={"pk": "metadata", "sk": "table_version"})
        value = result["Item"]["value"]
        return int(value)

    @cached_property
    def resource(self):
        return boto3.resource("dynamodb")

    @cached_property
    def table(self):
        return self.resource.Table(self.name)

    # scan ends up being the best option because there isn't an easy way to query
    # for all of the membership records in one go
    def get_data(self):
        i = 1

        print("Getting page", i)
        response = self.table.scan()
        yield from response["Items"]
        while key := response.get("LastEvaluatedKey"):
            i += 1
            print("Getting page", i)
            response = self.table.scan(ExclusiveStartKey=key)
            yield from response["Items"]

    def dump(self, filename: str):
        data = list(self.get_data())

        with open(filename, "w") as f:
            json.dump(data, f, cls=JSONEncoder)

    def populate(self, data: list[dict]):
        with self.table.batch_writer() as batch:
            for item in data:
                batch.put_item(Item=item)


def sorted_groupby(it, key):
    yield from groupby(sorted(it, key=key), key=key)


flatten = chain.from_iterable


def compose(*funcs):
    if not funcs:
        return lambda x: x

    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


class JSONEncoder(json.JSONEncoder):
    """For serializing Decimal and boto3:s Binary"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, boto3.dynamodb.types.Binary):
            return obj.value.decode("utf-8")
        return super().default(obj)


TABLES = {
    "songs": Table("songs", 1),
    "songs_v2": Table("songs_v2", 2),
    "songs_test": Table("songs_test", 2),
}


table_names = (
    "songs",
    "songs_v2",
    "songs_test",
)

TABLES_2 = {name: T2(name) for name in table_names}
