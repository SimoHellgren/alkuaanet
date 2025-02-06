from functools import partial
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
        for x in records
    ]

    return InlineKeyboardMarkup(buttons)


async def song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # allows using the same handler for both CommandHanlder and MessageHandler
    # maybe there's a way to distinguish this from the context?
    query = context.args[0] if context.args else update.message.text

    results = api.search("song", query)

    if not results:
        await update.message.reply_markdown_v2(f"No results for *{query}*")

    else:
        await update.message.reply_markdown_v2(
            f"Results for *{query}*", reply_markup=make_keyboard("song", results)
        )


async def search_group(kind: str, update: Update, context: ContextTypes) -> None:
    query = " ".join(context.args)

    results = api.search(kind, query)

    if not results:
        await update.message.reply_markdown_v2(f"No results for **{query}**")
    else:
        await update.message.reply_markdown_v2(
            f"Results for **{query}**", reply_markup=make_keyboard(kind, results)
        )


async def fetch_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    kind, id = query.data.split(":")

    if kind == "song":
        song = api.get_song(id)

        await query.message.reply_text(f"{song["name"]}\n{song["tones"]}")
        await query.message.reply_voice(song["opus"])

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
app.add_handler(CommandHandler("song", song))
app.add_handler(CommandHandler("composer", partial(search_group, "composer")))
app.add_handler(CommandHandler("collection", partial(search_group, "collection")))
app.add_handler(MessageHandler(filters.TEXT, song))
app.add_handler(CallbackQueryHandler(fetch_song))

app.run_polling()
