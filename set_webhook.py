"""TODO: see if this can be automated"""

import os

import dotenv
import requests

dotenv.load_dotenv()

LAMBDA_URL = os.environ.get("LAMBDA_URL")
TOKEN = os.environ.get("BOT_TOKEN")

requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")  # noqa: S113
requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={LAMBDA_URL}")  # noqa: S113
