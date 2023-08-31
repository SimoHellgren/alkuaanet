import logging
from time import gmtime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from .service import SongsAPI
from .config import token, apiurl

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

api = SongsAPI(apiurl)
bot = telepot.Bot(token)


def basic_keyboard(data, kind):
    buttons = [
        [InlineKeyboardButton(text=d["name"], callback_data=f"{kind}_{d['id']}")]
        for d in data
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def composer_keyboard(composers):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{c['lastname']}, {c['firstname']}",
                callback_data=f"composer_{c['id']}",
            )
        ]
        for c in composers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def on_chat(message):
    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    command, _, args = text.partition(" ")

    if text == "/start":
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

    elif text.startswith("/collections"):
        query = f"name startswith '{args}'" if args else {}
        collections = api.get_collections(params={"filter": query})

        kb = basic_keyboard(collections, "collection")
        bot.sendMessage(chat_id, "Collections", reply_markup=kb)

    elif text.startswith("/composers"):
        filt = f"lastname startswith '{args}'" if args else {}
        composers = api.get_composers(params={"filter": filt})

        kb = composer_keyboard(
            sorted(composers, key=lambda x: (x["lastname"], x["firstname"] or ""))
        )

        bot.sendMessage(chat_id, "Composers", reply_markup=kb)

    else:
        if text.startswith("!"):
            query = f"not (name startswith '{text[1:]}')"
        else:
            query = f"name startswith '{text}'"

        songs = sorted(
            api.get_songs(params={"filter": query}),
            key=lambda x: x["name"],
        )

        if songs:
            kb = basic_keyboard(songs, "song")
            bot.sendMessage(chat_id, f"Results for {text}", reply_markup=kb)
        else:
            bot.sendMessage(chat_id, f"No results for {text}")


def song_to_message(song):
    keys = "name", "tones"

    return "\n".join(f"{k}: {song.get(k)}" for k in keys)


def on_callback(message):
    query_id, chat_id, callback = telepot.glance(message, flavor="callback_query")

    kind, rid = callback.split("_")

    if kind == "song":
        song = api.get_song(rid)

        log.info(
            f"kind={kind!r} id={song['id']!r} name={song['name']!r} chat={chat_id!r}"
        )
        opus = api.get_song_opus(rid)
        bot.sendMessage(chat_id, song_to_message(song))
        bot.sendVoice(chat_id, opus)

    elif kind == "collection":
        songs = sorted(api.get_collection_songs(rid), key=lambda x: x["name"])

        if songs:
            kb = basic_keyboard(songs, "song")
            bot.sendMessage(chat_id, f"Songs in collection:", reply_markup=kb)
        else:
            bot.sendMessage(chat_id, f"No songs in collection")

    elif kind == "composer":
        songs = sorted(api.get_composer_songs(rid), key=lambda x: x["name"])

        if songs:
            kb = basic_keyboard(songs, "song")
            bot.sendMessage(chat_id, f"Songs by composer:", reply_markup=kb)
        else:
            bot.sendMessage(chat_id, f"No songs by composer")


message_loop = MessageLoop(bot, {"chat": on_chat, "callback_query": on_callback})
