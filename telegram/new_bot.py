from functools import partial
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
import os
import lib.service as api


load_dotenv()
TOKEN = os.environ["DEV_BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    await update.message.reply_text(msg)


def make_keyboard(kind: str, records: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(x["name"], callback_data=f"{kind}:{x["id"]}")]
        for x in sorted(records, key=lambda x: x["name"])
    ]

    return InlineKeyboardMarkup(buttons)


async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # allows usage from both CommandHandler and MessageHandler
    query = " ".join(context.args or []) or update.message.text

    results = api.search("song", query)

    if not results:
        await update.message.reply_markdown_v2(f"No results for _{query}_")

    else:
        await update.message.reply_markdown_v2(
            f"Results for _{query}_", reply_markup=make_keyboard("song", results)
        )


async def send_song(song: dict, message: Message) -> None:
    await message.reply_text(f"{song["name"]}\n{song["tones"]}")
    await message.reply_voice(song["opus"])


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_song(api.get_random_song(), update.message)


async def search_group(kind: str, update: Update, context: ContextTypes) -> None:
    query = " ".join(context.args)

    results = api.search(kind, query)

    if not results:
        await update.message.reply_markdown_v2(f"No results for _{kind} {query}_")
    else:
        await update.message.reply_markdown_v2(
            f"Results for _{kind} {query}_", reply_markup=make_keyboard(kind, results)
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    kind, id = query.data.split(":")

    if kind == "song":
        await send_song(api.get_song(id), query.message)

    if kind in ("composer", "collection"):
        songs = api.get_songlist(query.data)

        if not songs:
            await query.message.reply_markdown_v2(f"No songs")
        else:
            await query.message.reply_markdown_v2(
                "Songs:", reply_markup=make_keyboard("song", songs)
            )


app = ApplicationBuilder().token(TOKEN).build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("song", search_song))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("composers", partial(search_group, "composer")))
app.add_handler(CommandHandler("collections", partial(search_group, "collection")))
app.add_handler(MessageHandler(filters.TEXT, search_song))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_polling()
