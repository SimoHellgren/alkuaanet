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


def get_by_pk(item_id):
    """item_id example: song:1"""
    result = table.query(
        KeyConditionExpression=f"pk = :id",
        ExpressionAttributeValues={":id": item_id},
    )

    return result
