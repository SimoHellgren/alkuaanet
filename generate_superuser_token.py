from base64 import b64encode
import os
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

FERNET_KEY = os.environ["FERNET_KEY"]

fernet = Fernet(FERNET_KEY)

token = secrets.token_urlsafe(32).encode("utf-8")
encrypted = fernet.encrypt(token)
encoded = b64encode(encrypted)

print(encoded)
