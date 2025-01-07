"""default implementations for CRUD"""

from decimal import Decimal
from random import random
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

    # TODO: add proper "ModelCreate" to annotate `data`
    def create(self, table, data) -> Model:
        new_id = self._get_next_id(table)

        item_in = {
            "pk": self.model.__kind__,
            "sk": f"{self.model.__kind__}:{new_id}",
            "random": Decimal(
                str(random())
            ),  # not sure if this should be generated here
            **data.model_dump(),
        }

        response = table.put_item(Item=item_in)

        # TODO: might want to check for errors here

        return self.model(**item_in)

    def delete(self, table, id: int) -> "list[dict]":
        """Use `reverse-index` to get the primary keys of
        1. the record itself
        2. all relationships the record has.

        Then, delete all of the above
        """
        result = table.query(
            IndexName="reverse-index",
            KeyConditionExpression="sk = :id",
            ExpressionAttributeValues={":id": f"{self.model.__kind__}:{id}"},
        )

        # technically no need to "filter" `item` here, since reverse-index projects (return)
        # KEYS_ONLY, but just in case that changes
        keys = [
            {"pk": item["pk"], "sk": item["sk"]} for item in result.get("Items", [])
        ]

        deleted = [table.delete_item(Key=key, ReturnValues="ALL_OLD") for key in keys]

        return deleted

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
