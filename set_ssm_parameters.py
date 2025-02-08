import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
FERNET_KEY = os.environ["FERNET_KEY"]

ssm = boto3.client("ssm")

ssm.put_parameter(Name="alkuaanet-telegram-bot-token", Value=BOT_TOKEN, Overwrite=True)

ssm.put_parameter(Name="alkuaanet-fernet-key", Value=FERNET_KEY, Overwrite=True)
