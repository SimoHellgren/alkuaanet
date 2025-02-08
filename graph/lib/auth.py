from cryptography.fernet import Fernet
import boto3
from .dynamodb import get_item

ssm = boto3.client("ssm")
token_param = ssm.get_parameter(Name="alkuaanet-fernet-key", WithDecryption=True)
FERNET_KEY = token_param["Parameter"]["Value"]


def check_superuser_token(token: str) -> bool:
    fernet = Fernet(FERNET_KEY)
    superusertoken = get_item("token", "superuser")["value"].value
    return token == fernet.decrypt(superusertoken).decode("utf-8")
