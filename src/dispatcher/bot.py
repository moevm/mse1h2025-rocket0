from __future__ import annotations

from rocketchat_async import RocketChat as RocketChatAsync
from rocketchat_API.rocketchat import RocketChat
from typing import Callable, TYPE_CHECKING
from functools import partial
from pydantic import BaseModel
from models.enums import EventType
from handler import Handler, CallbackType
import asyncio
import uuid


if TYPE_CHECKING:
    from handler.filters import HandlerFilter
    from models.dto import RequestContext


class Bot[T: BaseModel]:
    def __init__(self, server_url: str, username: str, password: str) -> None:
        self._server_url: str = server_url
        self._username: str = username
        self._password: str = password

        self.async_client: RocketChatAsync = RocketChatAsync()
        self.sync_client: RocketChat = RocketChat(username, password, server_url=f'http://{server_url}')

        self.local_id: uuid.UUID = uuid.uuid4()
        self.id: str = self.sync_client.me().json()["_id"]

        self._handlers: list[Handler] = []

    async def run(self, callback: Callable[..., None]) -> None:
        attempts: int = 5
        while attempts > 0:
            try:
                await self.async_client.start(f'ws://{self._server_url}/websocket', self._username, self._password)

                for channel_id, _ in await self.async_client.get_channels():
                    await self.async_client.subscribe_to_channel_messages(
                        channel_id, partial(callback, self.local_id, EventType.MESSAGE)
                    )

                await self.async_client.run_forever()
            except (RocketChatAsync.ConnectionClosed, RocketChatAsync.ConnectCallFailed):
                await asyncio.sleep(3)
                attempts -= 1

    def register_handler(self, callback: CallbackType, input_type: type[T], filters: list[HandlerFilter]) -> None:
        self._handlers.append(Handler(callback, self, input_type, filters))

    async def resolve_handler(self, ctx: RequestContext) -> None:
        for handler in self._handlers:
            if handler.check(ctx):
                await handler.handle(ctx)

    async def send_message(self, text: str, channel_id: str, thread_id: str | None = None) -> None:
        await self.async_client.send_message(text, channel_id, thread_id)
