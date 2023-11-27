from lib.main import bot
import json


def handler(event, context):
    data = json.loads(event["body"])

    if "message" in data:
        kind = "message"

    elif "callback_query" in data:
        kind = "callback_query"

    else:
        kind = None

    if kind:
        bot.handle(data[kind])
