from telepot.loop import MessageLoop
from lib.main import bot
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.environ["DEV_BOT_TOKEN"]

# hacky but works lol
bot._token = TOKEN

MessageLoop(bot).run_as_thread()
