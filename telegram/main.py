import logging
from time import gmtime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from . import service as graph
from .config import token

# todo: logging configuration into separate module or config
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

log_formatter = logging.Formatter(
    "[%(asctime)s] {%(name)s} %(levelname)s - %(message)s"
)
log_formatter.converter = gmtime

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(log_formatter)
# log.addHandler(stream_handler)

file_handler = logging.FileHandler("./telegram/songs.log")
file_handler.setFormatter(log_formatter)
log.addHandler(file_handler)

bot = telepot.Bot(token)


def reply_keyboard(data):
    buttons = [
        [InlineKeyboardButton(text=d["name"], callback_data=d["id"])] for d in data
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


COMMANDS = {
    "/composers": graph.Kind.composer,
    "/collections": graph.Kind.collection,
    "/song": graph.Kind.song,
}


def handle_search_command(command, args):
    kind = COMMANDS.get(command)

    # this is a touch ugly
    if not kind:
        kind = graph.Kind.song
        args = command

    data = graph.search(kind, args)

    if data:
        kb = reply_keyboard(data)
        msg = f"Results for {kind} {args}"
    else:
        kb = None
        msg = f"No results for {kind} {args}"

    return msg, kb


def on_chat(message):
    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    command, _, args = text.partition(" ")

    # TODO: refactor command handling to be uniform
    if command == "/start":
        msg = (
            "Tervetuloa alkuäänibottiin!\n\n"
            "Botti hakee biisejä, säveltäjiä ja kokoelmia. Testaa esimerkiksi:\n\n"
            "hän\n"
            "/collections\n"
            "/collections p\n"
            "/composers\n"
            "/composers kuu\n"
        )

        bot.sendMessage(chat_id, msg)

    else:
        msg, kb = handle_search_command(command, args)
        bot.sendMessage(chat_id, msg, reply_markup=kb)


def song_to_message(song):
    keys = "name", "tones"

    return "\n".join(f"{k}: {song.get(k)}" for k in keys)


def on_callback(message):
    _, chat_id, callback = telepot.glance(message, flavor="callback_query")

    kind, _ = callback.split(":")

    if kind == "song":
        song = graph.get_song(callback)

        bot.sendMessage(chat_id, song_to_message(song))
        bot.sendVoice(chat_id, song["opus"])

    else:
        songs = graph.get_songlist(callback)

        if songs:
            kb = reply_keyboard(sorted(songs, key=lambda x: x["name"]))
            bot.sendMessage(chat_id, "Results:", reply_markup=kb)
        else:
            bot.sendMessage(chat_id, "No results")


message_loop = MessageLoop(bot, {"chat": on_chat, "callback_query": on_callback})
