import boto3

client = boto3.resource("dynamodb")

table = client.Table("songs")


def search(kind: str, string: str):
    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :kind AND begins_with(sk, :s)",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={":kind": kind, ":s": string},
    )

    return result


def get_by_pk(item_id: str, sort_key: str):
    """item_id example: song:1"""
    result = table.query(
        KeyConditionExpression=f"pk = :id and begins_with(sk, :sort_key)",
        ExpressionAttributeValues={":id": item_id, ":sort_key": sort_key},
    )

    return result


def get_opus(tones):
    result = table.query(
        KeyConditionExpression=f"pk = :pk and sk = :sort_key",
        ExpressionAttributeValues={":pk": "opus", ":sort_key": tones},
    )

    return result["Items"][0]["opus"].value.decode("utf-8")
