"""default implementations for CRUD"""

from typing import Protocol, ClassVar
from lib.models import Song, SearchResult

# TODO: improve typing with python 3.13 generics


class Model(Protocol):
    __kind__: ClassVar[str]


class CRUDBase:
    def __init__(self, model: Model):
        self.model = model

    def list(self, table) -> list[Model]:
        result = table.query(
            KeyConditionExpression="pk = :kind",
            ExpressionAttributeValues={":kind": self.model.__kind__},
        )

        return [self.model(**item) for item in result["Items"]]

    def search(self, table, string: str) -> "list[SearchResult]":
        result = table.query(
            IndexName="search_index",
            KeyConditionExpression="pk = :kind AND begins_with(search_name, :s)",
            ExpressionAttributeValues={":kind": self.model.__kind__, ":s": string},
        )

        return [SearchResult(**item) for item in result["Items"]]

    def get(self, table, id: int) -> Model | None:
        result = table.get_item(
            Key={
                "pk": self.model.__kind__,
                "sk": f"{self.model.__kind__}:{id}",
            }
        )

        item = result.get("Item")
        if item:
            return self.model(**item)

        return None

    def create(self, table, data):
        pass

    def _peek_sequence(self, table) -> int:
        """Utility for checking what the current_value of this record type's sequence is"""
        result = table.get_item(
            Key={"pk": "sequence", "sk": f"{self.model.__kind__}_id"}
        )

        return int(result["Item"]["current_value"])

    def _get_next_id(self, table) -> int:
        """Increments the sequence value and returns it"""
        response = table.update_item(
            Key={
                "pk": "sequence",
                "sk": f"{self.model.__kind__}_id",
            },
            ReturnValues="ALL_NEW",
            UpdateExpression="SET current_value = current_value + :incr",
            ExpressionAttributeValues={":incr": 1},
        )

        num = int(response["Attributes"]["current_value"])

        return num


class Group(CRUDBase):
    """Extends Base with ability to list songs"""

    def list_songs(self, table, id: int) -> list[SearchResult]:
        result = table.query(
            KeyConditionExpression="pk = :kind",
            ExpressionAttributeValues={":kind": f"{self.model.__kind__}:{id}"},
        )

        return [SearchResult(**item) for item in result["Items"]]
