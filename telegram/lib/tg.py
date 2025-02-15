import json
from enum import StrEnum, auto
from functools import partialmethod
from typing import Any, BinaryIO, Callable, Self

import httpx
from pydantic import BaseModel

type Handler[Kind] = Callable[[Bot, Kind], None]


class ParseMode(StrEnum):
    MarkdownV2 = auto()
    HTML = auto()
    Markdown = auto()


class Bot:
    def __init__(self, token: str) -> Self:
        self.token = token

    def request(
        self, method: str, endpoint: str, **kwargs: dict[str, Any]
    ) -> httpx.Response:
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
        reply_markup: dict | None = None,
    ) -> None:
        return self.post(
            "sendMessage",
            params={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "reply_markup": json.dumps(reply_markup) if reply_markup else None,
            },
        )

    def send_voice(
        self,
        chat_id: int,
        voice: BinaryIO,
        caption: str = "",
        parse_mode: ParseMode | None = None,
    ) -> None:
        return self.post(
            "sendVoice",
            params={
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": parse_mode,
            },
            files={
                "voice": (
                    "applicaton.octet-stream",
                    voice.read(),
                    "application/octet-stream",
                )
            },
        )

    def answer_callback_query(self, chat_id: int, callback_query_id: int) -> None:
        return self.post(
            "answerCallbackQuery",
            params={"chat_id": chat_id, "callback_query_id": callback_query_id},
        )


def make_keyboard(kind: str, data: list[dict]) -> dict:
    keys = [
        [{"text": datum["name"], "callback_data": f"{kind}:{datum['id']}"}]
        for datum in data
    ]
    return {"inline_keyboard": keys}


class Chat(BaseModel):
    id: int


class Entity(BaseModel):
    type: str


class Command(BaseModel):
    name: str
    args: list[str]
    chat: Chat

    @classmethod
    def from_message(cls, message: "Message") -> Self:
        command, _, args = message.text.partition(" ")
        return cls(name=command, args=args.split(), chat=message.chat)


class Message(BaseModel):
    chat: Chat
    text: str
    entities: list[Entity] | None = None

    @property
    def is_command(self) -> bool:
        if not self.entities:
            return False

        return any(e.type == "bot_command" for e in self.entities)

    @property
    def command(self) -> Command | None:
        if self.is_command:
            return Command.from_message(self)

        return None


class CallbackQuery(BaseModel):
    id: int
    data: str
    message: Message


class Update(BaseModel):
    update_id: int
    message: Message | None = None
    callback_query: CallbackQuery | None = None


class App:
    """Binds a bot and handlers in a nice bundle :3"""

    def __init__(
        self,
        bot: Bot,
        message_handler: Handler[Message],
        command_handlers: dict[str, Handler[Command]],
        callback_handler: Handler[CallbackQuery],
    ) -> Self:
        self.bot = bot
        self.message_handler = message_handler
        self.command_handlers = command_handlers
        self.callback_handler = callback_handler

    def process_update(self, update: dict) -> None:
        u = Update(**update)

        if u.message:
            if u.message.is_command:
                command = self.command_handlers.get(u.message.command.name)
                if command:
                    command(self.bot, u.message.command)
                else:
                    # if command not found, default to message_handler
                    self.message_handler(self.bot, u.message)
            else:
                self.message_handler(self.bot, u.message)

        elif u.callback_query:
            self.callback_handler(self.bot, u.callback_query)

    def get_updates(self, **kwargs: dict[str, Any]) -> list[dict]:
        return self.bot.get_updates(**kwargs)
