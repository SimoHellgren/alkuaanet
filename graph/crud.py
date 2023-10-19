import boto3

client = boto3.resource("dynamodb")

table = client.Table("songs")


def search_songs(string):
    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :kind AND begins_with(sk, :s)",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={":kind": "song", ":s": string},
    )

    return result


def get_by_pk(item_id):
    """item_id example: song:1"""
    result = table.query(
        KeyConditionExpression=f"pk = :id",
        ExpressionAttributeValues={":id": item_id},
    )

    return result


def get_songs():
    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :kind",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={":kind": "song"},
    )

    return result
