from lib.bot import get_app
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.environ["DEV_BOT_TOKEN"]

app = get_app(TOKEN)

print("Running in dev mode!")
app.run_polling()
