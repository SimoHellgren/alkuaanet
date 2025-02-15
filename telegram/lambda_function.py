import json
import logging

import boto3
from app import build_app

# suppress httpx logs to avoid logging apikey
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


ssm = boto3.client("ssm")
token_param = ssm.get_parameter(
    Name="alkuaanet-telegram-bot-token",
    WithDecryption=True,
)
TOKEN = token_param["Parameter"]["Value"]
app = build_app(TOKEN)


def handler(event, context) -> None:  # noqa: ANN001 ARG001
    log.info(event["body"], extra={"type": "telegram.update"})
    data = json.loads(event["body"])

    app.process_update(data)
