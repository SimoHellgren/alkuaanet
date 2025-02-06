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


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.name}")


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


async def song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # allows using the same handler for both CommandHanlder and MessageHandler
    # maybe there's a way to distinguish this from the context?
    q = context.args[0] if context.args else update.message.text

    results = api.search("song", q)

    if not results:
        await update.message.reply_markdown_v2(f"No results for *{q}*")

    else:
        keys = [
            [InlineKeyboardButton(song["name"], callback_data=f"song:{song["id"]}")]
            for song in results
        ]

        await update.message.reply_markdown_v2(
            f"Results for *{q}*", reply_markup=InlineKeyboardMarkup(keys)
        )


async def fetch_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    kind, id = query.data.split(":")

    if kind == "song":
        song = api.get_song(id)

        await query.message.reply_text(f"{song["name"]}\n{song["tones"]}")
        await query.message.reply_voice(song["opus"])


app = ApplicationBuilder().token(TOKEN).build()

COMMANDS = [
    hello,
    start,
    song,
]

for command in COMMANDS:
    app.add_handler(CommandHandler(command.__name__, command))

app.add_handler(MessageHandler(filters.TEXT, song))
app.add_handler(CallbackQueryHandler(fetch_song))

app.run_polling()
