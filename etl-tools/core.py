from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property, reduce
from itertools import chain, groupby
from pathlib import Path
from typing import TypeAlias, Iterable, Generator
import json
import boto3
import boto3.dynamodb.types


class VersionNotFound(Exception):
    pass


Dump: TypeAlias = Iterable[dict]


def load_dump(file: Path) -> Dump:
    with open(file) as f:
        # parse numbers to Decimal, because that is what DynamoDB wants
        data = json.load(f, parse_float=Decimal, parse_int=Decimal)

    return data


@dataclass
class Table:
    name: str

    @cached_property
    def version(self) -> int:
        result = self.table.get_item(Key={"pk": "metadata", "sk": "table_version"})
        try:
            value = result["Item"]["value"]
            return int(value)
        except KeyError:
            raise VersionNotFound(f"Table {self.name} has no metadata for version.")

    @cached_property
    def resource(self):
        return boto3.resource("dynamodb")

    @cached_property
    def table(self):
        return self.resource.Table(self.name)

    # scan ends up being the best option because there isn't an easy way to query
    # for all of the membership records in one go
    def get_data(self) -> Generator[dict, None, None]:
        i = 1

        print("Getting page", i)
        response = self.table.scan()
        yield from response["Items"]
        while key := response.get("LastEvaluatedKey"):
            i += 1
            print("Getting page", i)
            response = self.table.scan(ExclusiveStartKey=key)
            yield from response["Items"]

    def dump(self, filename: str) -> None:
        data = list(self.get_data())

        with open(filename, "w") as f:
            json.dump(data, f, cls=JSONEncoder)

    def populate(self, data: Iterable[dict]) -> None:
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


table_names = (
    "songs",
    "songs_v2",
    "songs_test",
)

TABLES = {name: Table(name) for name in table_names}
