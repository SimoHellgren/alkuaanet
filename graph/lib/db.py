"""Models to interact with DynamoDB"""

import boto3


class Base:
    def __init__(self, table, kind):
        self.table = table
        self.kind = kind

    def list(self):
        result = self.table.query(
            KeyConditionExpression="pk = :kind",
            ExpressionAttributeValues={":kind": self.kind},
        )

        return result["Items"]

    def search(self, string: str):
        result = self.table.query(
            IndexName="search_index",
            KeyConditionExpression="pk = :kind AND begins_with(search_name, :s)",
            ExpressionAttributeValues={":kind": self.kind, ":s": string},
        )

        return result["Items"]

    def get(self, id: int):
        result = self.table.get_item(
            Key={
                "pk": self.kind,
                "sk": f"{self.kind}:{id}",
            }
        )

        return result.get("Item")

    def create(self, data):
        pass

    def _peek_sequence(self):
        """Utility for checking what the current_value of this record type's sequence is"""
        result = self.table.get_item(Key={"pk": "sequence", "sk": f"{self.kind}_id"})

        return int(result["Item"]["current_value"])

    def _get_next_id(self):
        """Increments the sequence value and returns it"""
        response = table.update_item(
            Key={
                "pk": "sequence",
                "sk": f"{self.kind}_id",
            },
            ReturnValues="ALL_NEW",
            UpdateExpression="SET current_value = current_value + :incr",
            ExpressionAttributeValues={":incr": 1},
        )

        num = int(response["Attributes"]["current_value"])

        return num


class Group(Base):
    """Extends Base with ability to list songs"""

    def __init__(self, table, kind):
        super().__init__(table, kind)

    def list_songs(self, id):
        result = self.table.query(
            KeyConditionExpression="pk = :kind",
            ExpressionAttributeValues={":kind": f"{self.kind}:{id}"},
        )

        return result["Items"]


class Opus:
    def __init__(self, table):
        self.table = table

    def get(self, tones: str):
        result = self.table.get_item(
            Key={
                "pk": "opus",
                "sk": tones,
            }
        )

        return result.get("Item")


if __name__ == "__main__":
    table = boto3.resource("dynamodb").Table("songs_v2")

    songs = Base(table, "song")
    collections = Group(table, "collection")
    composers = Group(table, "composer")

    opus = Opus(table)
