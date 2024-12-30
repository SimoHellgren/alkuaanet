"""TODO: see if this can be automated"""

import dotenv

dotenv.load_dotenv()

from telegram.lib.main import bot
import os


API_URL = os.environ.get("API_URL")
bot.deleteWebhook()
bot.setWebhook(API_URL)
