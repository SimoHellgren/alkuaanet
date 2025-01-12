import json
import boto3
from lib.models import Opus

LAMBDA = boto3.client("lambda")


class CRUDOpus:
    def get(self, table, tones: str) -> Opus | None:
        result = table.get_item(
            Key={
                "pk": "opus",
                "sk": tones,
            }
        )

        item = result.get("Item")

        if item:
            return Opus(**item)

        return None

    def create(self, table, tones: str):
        tones_list = tones.split("-")

        # no idea why the payload needs double json.dumps,
        # should probably figure that out
        response = LAMBDA.invoke(
            FunctionName="alkuaanet-synth",
            InvocationType="RequestResponse",
            Payload=json.dumps({"body": json.dumps({"tones": tones_list})}),
        )

        opus = json.loads(response["Payload"].read()).get("body")

        table.put_item(
            Item={
                "pk": "opus",
                "sk": tones,
                "opus": opus.encode("utf-8"),
            }
        )


opus = CRUDOpus()
