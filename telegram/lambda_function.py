from lib.main import bot
import json


def handler(event, context):
    data = json.loads(event["body"])
    chat_id = data["message"]["chat"]["id"]
    message = data["message"]["text"]

    bot.sendMessage(chat_id, message)
