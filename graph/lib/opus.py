"""It is debatable whether this should be its own module or a part of crud.py"""

import json
import boto3
from . import dynamodb as db

LAMBDA = boto3.client("lambda")


def get(tones: str) -> dict | None:
    return db.get_item("opus", tones)


def create(tones: str) -> None:
    tones_list = tones.split("-")

    # no idea why the payload needs double json.dumps,
    # should probably figure that out
    response = LAMBDA.invoke(
        FunctionName="alkuaanet-synth",
        InvocationType="RequestResponse",
        Payload=json.dumps({"body": json.dumps({"tones": tones_list})}),
    )

    opus = json.loads(response["Payload"].read()).get("body")

    db.put(
        {
            "pk": "opus",
            "sk": tones,
            "opus": opus.encode("utf-8"),
        }
    )
