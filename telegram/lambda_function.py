import asyncio
import json
import logging
import boto3
from telegram import Update
from lib.bot import get_app

# suppress httpx logs to avoid logging apikey
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger()


ssm = boto3.client("ssm")
token_param = ssm.get_parameter(
    Name="alkuaanet-telegram-bot-token", WithDecryption=True
)
TOKEN = token_param["Parameter"]["Value"]


async def process_event(update_dict: dict):
    app = get_app(TOKEN)
    update = Update.de_json(update_dict, app.bot)  # no idea why, but yes.

    await app.initialize()

    await app.process_update(update)


def handler(event, context):
    log.info(event["body"])
    data = json.loads(event["body"])

    return asyncio.get_event_loop().run_until_complete(process_event(data))
