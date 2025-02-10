from enum import Enum, auto
import os
from dotenv import load_dotenv
from lib.tg import Bot
from lib import service as api

load_dotenv(override=True)
TOKEN = os.environ.get("DEV_BOT_TOKEN")
bot = Bot(TOKEN)


def parse_command(text: str) -> tuple[str, list[str]]:
    command, _, args = text.partition(" ")

    return command, args.split()


def extract_chat_id(update: dict) -> int:
    match flavor(update):
        case Flavor.message | Flavor.command:
            return update["message"]["chat"]["id"]
        case Flavor.callback:
            return update["callback_query"]["message"]["chat"]["id"]


class Flavor(Enum):
    message = auto()
    callback = auto()
    command = auto()
    unknown = auto()


def flavor(update: dict) -> Flavor:
    if "message" in update:
        if entities := update["message"].get("entities"):
            if any(e["type"] == "bot_command" for e in entities):
                return Flavor.command

        return Flavor.message

    if "callback_query" in update:
        return Flavor.callback

    return Flavor.unknown


def start(update: dict, args=None) -> None:
    chat_id = extract_chat_id(update)
    msg = (
        "Tervetuloa alkuäänibottiin!\n\n"
        "Botti hakee biisejä, säveltäjiä ja kokoelmia. Testaa esimerkiksi:\n\n"
        "hän\n"
        "/collections\n"
        "/collections p\n"
        "/composers\n"
        "/composers kuu\n"
        "/random"
    )

    # parse_mode = None due to not wanting to escape exclamation marks
    return bot.send_message(chat_id, msg, parse_mode=None)


def handle_callback(update: dict) -> None:
    chat_id = extract_chat_id(update)
    kind, id = update["callback_query"]["data"].split(":")

    match kind:
        case "song":
            song = api.get_song(int(id))
            bot.send_voice(chat_id, song["opus"], f"{song["name"]}: {song["tones"]}")


def handle_message(update: dict) -> None:
    chat_id = extract_chat_id(update)

    songs = api.search("song", update["message"]["text"])
    for song in songs:
        bot.send_message(chat_id, song["name"])


def handle_command(update: dict) -> None:
    command, args = parse_command(update["message"]["text"])

    COMMANDS = {"/start": start}

    return COMMANDS[command](update, args)


def process_update(update: dict) -> None:
    match flavor(update):
        case Flavor.command:
            handle_command(update)

        case Flavor.message:
            handle_message(update)

        case Flavor.callback:
            handle_callback(update)
