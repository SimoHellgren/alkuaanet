from lib import service as api
from lib.tg import App, Bot, Message, CallbackQuery, Command, make_keyboard, ParseMode


def handle_message(bot: Bot, message: Message) -> None:
    songs = api.search("song", message.text)
    keyboard = make_keyboard("song", songs)
    bot.send_message(
        message.chat.id, f"Results for _song {message.text}_", reply_markup=keyboard
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
        "/random"
    )

    # parse_mode = None due to not wanting to escape exclamation marks
    bot.send_message(command.chat.id, msg, parse_mode=None)


def send_song(
    bot: Bot, chat_id: int, song: dict, parse_mode: ParseMode | None = None
) -> None:
    bot.send_voice(
        chat_id, song["opus"], f"{song["name"]}: {song["tones"]}", parse_mode=parse_mode
    )


def handle_random(bot: Bot, command: Command) -> None:
    song = api.get_random_song()
    send_song(bot, command.chat.id, song)


def handle_guess(bot: Bot, command: Command) -> None:
    song = api.get_random_song()
    # add spoiler to song name
    song["name"] = f"||{song["name"]}||"
    # escape dashes
    song["tones"] = song["tones"].replace("-", "\-")
    send_song(bot, command.chat.id, song, parse_mode=ParseMode.MarkdownV2)


def handle_search(bot: Bot, command: Command) -> None:
    kind = command.name[1:-1]  # ugly
    query = " ".join(command.args)
    results = api.search(kind, query)
    keyboard = make_keyboard(kind, results)

    if results:
        reply = f"Results for _{kind} {query}_:"
    else:
        reply = f"No results for _{kind} {query}_"

    bot.send_message(command.chat.id, reply, reply_markup=keyboard)


def handle_callback(bot: Bot, callback_query: CallbackQuery) -> None:
    kind, id = callback_query.data.split(":")

    chat_id = callback_query.message.chat.id

    match kind:
        case "song":
            song = api.get_song(int(id))
            send_song(bot, chat_id, song)
            bot.answer_callback_query(chat_id, callback_query.id)

        case "collection" | "composer":
            songs = api.get_songlist(callback_query.data)
            keyboard = make_keyboard("song", songs)
            bot.send_message(chat_id, "Songs:", reply_markup=keyboard)
            bot.answer_callback_query(chat_id, callback_query.id)


def build_app(token: str):
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
