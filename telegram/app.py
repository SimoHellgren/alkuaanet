import re

from lib import service as api
from lib.tg import App, Bot, CallbackQuery, Command, Message, ParseMode, make_keyboard


def handle_message(bot: Bot, message: Message) -> None:
    songs = api.search(api.Kind.song, message.text)
    keyboard = make_keyboard("song", songs)
    bot.send_message(
        message.chat.id,
        f"Results for _song {message.text}_",
        reply_markup=keyboard,
    )


def start(bot: Bot, command: Command) -> None:
    msg = (
        "Tervetuloa alkuäänibottiin!\n\n"
        "Botti hakee biisejä, säveltäjiä ja kokoelmia. Testaa esimerkiksi:\n\n"
        "hän\n"
        "/collections\n"
        "/collections p\n"
        "/composers\n"
        "/composers kuu\n"
        "/random\n"
        "/guess"
    )

    # parse_mode = None due to not wanting to escape exclamation marks
    bot.send_message(command.chat.id, msg, parse_mode=None)


def send_song(
    bot: Bot,
    chat_id: int,
    song: dict,
    parse_mode: ParseMode | None = None,
) -> None:
    bot.send_voice(
        chat_id,
        song["opus"],
        f"{song['name']}: {song['tones']}",
        parse_mode=parse_mode,
    )
    if song["id"] == 236:  # noqa: PLR2004
        bot.send_message(chat_id, "Missä on _näin_ hyvät bileet?")


def handle_random(bot: Bot, command: Command) -> None:
    song = api.get_random_song()
    send_song(bot, command.chat.id, song)


def escape(s: str) -> str:
    """Escapes special characters for MarkdownV2."""
    chars = "_*[]()~`>#+-=|{}.!"
    re_chars = "\\".join(chars)
    pattern = re.compile(f"([{re_chars}])")

    return pattern.sub(r"\\\1", s)


def handle_guess(bot: Bot, command: Command) -> None:
    song = api.get_random_song()
    # add spoiler to song name and escape special characters
    song["name"] = f"||{escape(song['name'])}||"
    song["tones"] = escape(song["tones"])
    send_song(bot, command.chat.id, song, parse_mode=ParseMode.MarkdownV2)


def handle_search(bot: Bot, command: Command) -> None:
    kind = api.Kind(command.name[1:-1])  # slice a bit ugly

    query = " ".join(command.args)
    results = api.search(kind, query)
    keyboard = make_keyboard(kind, results)

    if results:
        reply = f"Results for _{kind} {query}_:"
    else:
        reply = f"No results for _{kind} {query}_"

    bot.send_message(command.chat.id, reply, reply_markup=keyboard)


def handle_callback(bot: Bot, callback_query: CallbackQuery) -> None:
    kind, record_id = callback_query.data.split(":")

    chat_id = callback_query.message.chat.id

    match kind:
        case "song":
            song = api.get_song(int(record_id))
            send_song(bot, chat_id, song)
            bot.answer_callback_query(chat_id, callback_query.id)

        case "collection" | "composer":
            songs = api.get_songlist(callback_query.data)
            keyboard = make_keyboard("song", songs)
            bot.send_message(chat_id, "Songs:", reply_markup=keyboard)
            bot.answer_callback_query(chat_id, callback_query.id)


def build_app(token: str) -> App:
    return App(
        Bot(token),
        handle_message,
        {
            "/start": start,
            "/random": handle_random,
            "/collections": handle_search,
            "/composers": handle_search,
            "/guess": handle_guess,
        },
        handle_callback,
    )
