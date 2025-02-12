from typing import Callable
from lib import service as api
from lib.tg import Bot, Update, Message, CallbackQuery, Command, make_keyboard


type Handler[Kind] = Callable[[Bot, Kind], None]


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


def send_song(bot: Bot, chat_id: int, song: dict) -> None:
    bot.send_voice(chat_id, song["opus"], f"{song["name"]}: {song["tones"]}")


def handle_random(bot: Bot, command: Command) -> None:
    song = api.get_random_song()
    send_song(bot, command.chat.id, song)


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


class App:
    def __init__(
        self,
        bot,
        message_handler: Handler[Message],
        command_handlers: dict[str, Handler[Command]],
        callback_handler: Handler[CallbackQuery],
    ):
        self.bot = bot
        self.message_handler = message_handler
        self.command_handlers = command_handlers
        self.callback_handler = callback_handler

    def process_update(self, update: dict):
        u = Update(**update)

        if u.message:
            if u.message.is_command:
                command = self.command_handlers[u.message.command.name]
                command(self.bot, u.message.command)
            else:
                self.message_handler(self.bot, u.message)

        elif u.callback_query:
            self.callback_handler(self.bot, u.callback_query)


if __name__ == "__main__":
    import os
    from time import sleep
    from dotenv import load_dotenv

    load_dotenv(override=True)

    TOKEN = os.environ.get("DEV_BOT_TOKEN")

    bot = Bot(TOKEN)
    app = App(
        bot,
        handle_message,
        {
            "/start": start,
            "/random": handle_random,
            "/collections": handle_search,
            "/composers": handle_search,
        },
        handle_callback,
    )

    max_update = -1
    print("Running...")
    while True:
        updates = (
            app.bot.get_updates(params={"offset": max_update + 1})
            .json()
            .get("result", [])
        )

        for update in updates:
            print("processing", update)
            app.process_update(update)

        if updates:
            max_update = max(u["update_id"] for u in updates)

        sleep(1)
