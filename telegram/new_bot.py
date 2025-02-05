from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.environ["DEV_BOT_TOKEN"]


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.name}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))


app.run_polling()
