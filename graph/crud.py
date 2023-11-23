import json
import boto3
from typing import Optional
from .hankkari import is_hankkari

dynamo = boto3.resource("dynamodb")

table = dynamo.Table("songs")

lambdafunc = boto3.client("lambda")


def search(kind: str, string: str):
    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :kind AND begins_with(sk, :s)",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={":kind": kind, ":s": string},
    )

    return result


def opus_exists(tones: str) -> bool:
    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :opus AND sk = :tones",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={":opus": "opus", ":tones": tones},
    )

    return result["Count"] > 0


def composer_exists(first_name: str, last_name: str) -> bool:
    name = ", ".join(filter(None, [last_name, first_name])).lower()

    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :composer AND sk = :name",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={":composer": "composer", ":name": "name:" + name},
    )

    return result["Count"] > 0


def collection_exists(name: str) -> bool:
    result = table.query(
        IndexName="LookupIndex",
        KeyConditionExpression="#PK = :collection AND sk = :name",
        ExpressionAttributeNames={"#PK": "type"},
        ExpressionAttributeValues={
            ":collection": "collection",
            ":name": "name:" + name.lower(),
        },
    )

    return result["Count"] > 0


def get_by_pk(item_id: str, sort_key: str):
    """item_id example: song:1"""
    result = table.query(
        KeyConditionExpression=f"pk = :id and begins_with(sk, :sort_key)",
        ExpressionAttributeValues={":id": item_id, ":sort_key": sort_key},
    )

    return result


def get_next_id(kind: str):
    """Gets the next id for song, composer or collection.
    Note that the id gets incremented regardless of whether
    you actually use it or not.
    """
    response = table.update_item(
        Key={
            "pk": "sequence",
            "sk": f"{kind}_id",
        },
        ReturnValues="ALL_NEW",
        UpdateExpression="SET current_value = current_value + :incr",
        ExpressionAttributeValues={":incr": 1},
    )

    num = response["Attributes"]["current_value"]

    return f"{kind}:{num}"


def create_composer(first_name: str, last_name: str):
    composer_id = get_next_id("composer")

    name = ", ".join(filter(None, [last_name, first_name]))

    item = {
        "pk": composer_id,
        "sk": "name:" + name.lower(),
        "first_name": first_name,
        "last_name": last_name,
        "name": name,
        "type": "composer",
    }

    composer = table.put_item(Item=item)

    return item


def create_collection(name: str):
    collection_id = get_next_id("collection")

    item = {
        "pk": collection_id,
        "sk": "name:" + name.lower(),
        "name": name,
        "type": "collection",
    }

    collection = table.put_item(Item=item)

    return item


def create_song(
    name: str,
    tones: str,
    composer: Optional[dict] = None,
    collections: Optional[list[str]] = None,
):
    song_id = get_next_id("song")

    item = {
        "pk": song_id,
        "sk": "name:" + name.lower(),
        "name": name,
        "tones": tones,
        "type": "song",
    }

    song = table.put_item(Item=item)

    # create opus if needed
    if not opus_exists(tones):
        create_opus(tones.split("-"))
        print("Created opus for", tones)
    else:
        print("Opus found for", tones)

    # assign composer
    if composer:
        first_name = composer.get("first_name")
        last_name = composer.get("last_name")
        # create if needed
        if not composer_exists(first_name, last_name):
            composer = create_composer(first_name, last_name)

        else:
            search_name = ", ".join(filter(None, [last_name, first_name])).lower()
            composer = search("composer", "name:" + search_name)["Items"][0]

        add_membership(composer["pk"], song_id)

    if collections:
        for collection_name in collections:
            # create if needed
            if not collection_exists(collection_name):
                collection = create_collection(collection_name)
            else:
                collection = search("collection", "name:" + collection_name.lower())[
                    "Items"
                ][0]

            add_membership(collection["pk"], song_id)

    # add to hankkari if is hankkari
    if is_hankkari(tones.split("-")):
        add_membership("collection:7", song_id)

    return item


def add_membership(from_id, to_id):
    to_item = get_by_pk(to_id, "name")["Items"][0]

    item = {
        "pk": from_id,
        "sk": to_id,
        "name": to_item["name"],
        "type": "membership",
    }

    membership = table.put_item(Item=item)

    return item


def get_opus(tones):
    result = table.query(
        KeyConditionExpression=f"pk = :pk and sk = :sort_key",
        ExpressionAttributeValues={":pk": "opus", ":sort_key": tones},
    )

    return result["Items"][0]["opus"].value.decode("utf-8")


def create_opus(tones: list):
    # no idea why the payload needs double json.dumps,
    # should probably figure that out
    response = lambdafunc.invoke(
        FunctionName="alkuaanet-synth",
        InvocationType="RequestResponse",
        Payload=json.dumps({"body": json.dumps({"tones": tones})}),
    )

    opus = json.loads(response["Payload"].read()).get("body")

    table.put_item(
        Item={
            "pk": "opus",
            "sk": "-".join(tones),
            "opus": opus.encode("utf-8"),
            "type": "opus",
        }
    )
