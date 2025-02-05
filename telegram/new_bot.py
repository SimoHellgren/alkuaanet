from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
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

    for song in results:
        await update.message.reply_text(song)


app = ApplicationBuilder().token(TOKEN).build()

COMMANDS = [
    hello,
    start,
    song,
]

for command in COMMANDS:
    app.add_handler(CommandHandler(command.__name__, command))

app.add_handler(MessageHandler(filters.TEXT, song))

app.run_polling()
