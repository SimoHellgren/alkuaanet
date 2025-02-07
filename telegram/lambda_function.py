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


async def process_event(event: dict):
    await app.initialize()

    await app.process_update(Update(**event))


def handler(event, context):
    log.info(event["body"])

    data = json.loads(event["body"])

    asyncio.run(process_event(data))
