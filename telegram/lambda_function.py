import asyncio
import json
import logging
import boto3
from telegram import Update
from lib.bot import get_app

log = logging.getLogger()


ssm = boto3.client("ssm")
token_param = ssm.get_parameter(
    Name="alkuaanet-telegram-bot-token", WithDecryption=True
)
TOKEN = token_param["Parameter"]["Value"]

app = get_app(TOKEN)


async def process_event(update_dict: dict):
    update = Update.de_json(update_dict, app.bot)  # no idea why, but yes.

    await app.initialize()

    await app.process_update(update)


def handler(event, context):
    log.info(event["body"])

    data = json.loads(event["body"])

    loop = asyncio.get_event_loop()

    loop.run_until_complete(process_event(data))
