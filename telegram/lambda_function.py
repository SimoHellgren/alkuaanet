from lib.main import bot
import json
import logging

log = logging.getLogger()


def handler(event, context):
    data = json.loads(event["body"])

    if "message" in data:
        kind = "message"
        log_type = "telegram.message"

    elif "callback_query" in data:
        kind = "callback_query"
        log_type = "telegram.callback"

    else:
        kind = None
        log_type = "telegram.unhandled"

    log.info(event["body"], extra={"type": log_type})

    if kind:
        bot.handle(data[kind])
