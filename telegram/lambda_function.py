from enum import Enum, auto
import json
import logging
import boto3
from lib import service as api
from lib.tg import Bot


# suppress httpx logs to avoid logging apikey
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


ssm = boto3.client("ssm")
token_param = ssm.get_parameter(
    Name="alkuaanet-telegram-bot-token", WithDecryption=True
)
TOKEN = token_param["Parameter"]["Value"]
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


def start(update: dict, args: list[str]) -> None:
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


def send_song(chat_id: int, song: dict) -> None:
    bot.send_voice(chat_id, song["opus"], f"{song["name"]}: {song["tones"]}")


def handle_random(update: dict) -> None:
    chat_id = extract_chat_id(update)
    song = api.get_random_song()
    send_song(chat_id, song)


def handle_callback(update: dict) -> None:
    chat_id = extract_chat_id(update)
    query_id = update["callback_query"]["id"]
    callback_data = update["callback_query"]["data"]
    kind, id = callback_data.split(":")

    match kind:
        case "song":
            song = api.get_song(int(id))
            send_song(chat_id, song)
            bot.answer_callback_query(chat_id, query_id)

        case "collection" | "composer":
            songs = api.get_songlist(callback_data)
            keyboard = make_keyboard("song", songs)
            bot.send_message(chat_id, "Songs:", reply_markup=keyboard)
            bot.answer_callback_query(chat_id, query_id)


def make_keyboard(kind: str, data: list[dict]) -> dict:
    keys = [
        [{"text": datum["name"], "callback_data": f"{kind}:{datum["id"]}"}]
        for datum in data
    ]
    return {"inline_keyboard": keys}


def handle_search(update: dict, kind: str, query: str) -> None:
    results = api.search(kind, query)
    keyboard = make_keyboard(kind, results)

    if results:
        reply = f"Results for _{kind} {query}_:"
    else:
        reply = f"No results for _{kind} {query}_"

    chat_id = extract_chat_id(update)
    bot.send_message(chat_id, reply, reply_markup=keyboard)


def handle_command(update: dict) -> None:
    command, args = parse_command(update["message"]["text"])

    match command:
        case "/start":
            start()

        case "/random":
            handle_random(update)

        case "/composers":
            handle_search(update, "composer", " ".join(args))

        case "/collections":
            handle_search(update, "collection", " ".join(args))


def process_update(update: dict) -> None:
    match flavor(update):
        case Flavor.command:
            handle_command(update)
        case Flavor.message:
            handle_search(update, "song", update["message"]["text"])

        case Flavor.callback:
            handle_callback(update)


def handler(event, context):
    log.info(event["body"], extra={"type": "telegram.update"})
    data = json.loads(event["body"])

    process_update(data)
