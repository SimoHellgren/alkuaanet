from enum import StrEnum, auto
from functools import partialmethod
from typing import BinaryIO
import httpx


class ParseMode(StrEnum):
    MarkdownV2 = auto()
    HTML = auto()
    Markdown = auto()


class Bot:
    def __init__(self, token):
        self.token = token

    def request(self, method, endpoint, **kwargs):
        base = f"https://api.telegram.org/bot{self.token}/"
        return httpx.request(method, base + endpoint, **kwargs)

    get = partialmethod(request, "GET")
    post = partialmethod(request, "POST")

    get_updates = partialmethod(get, "getUpdates")

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: ParseMode | None = ParseMode.MarkdownV2,
        reply_markup=None,
    ) -> None:
        return self.post(
            "sendMessage",
            params={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
        )

    def send_voice(self, chat_id: str, voice: BinaryIO, caption: str = ""):
        return self.post(
            "sendVoice",
            params={
                "chat_id": chat_id,
                "caption": caption,
            },
            files={
                "voice": (
                    "applicaton.octet-stream",
                    voice.read(),
                    "application/octet-stream",
                )
            },
        )
