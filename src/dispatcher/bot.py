from __future__ import annotations

from rocketchat_async import RocketChat as RocketChatAsync
from rocketchat_API.rocketchat import RocketChat
from typing import Callable, Any, TYPE_CHECKING
from functools import partial
from http import HTTPStatus
from pydantic import BaseModel
from models.enums import EventType, RoomType
from handler import Handler, CallbackType
from datetime import datetime, timezone
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

        self._local_id: uuid.UUID = uuid.uuid4()
        self._id: str = self.sync_client.me().json()["_id"]

        self._handlers: list[Handler] = []

    @property
    def local_id(self) -> uuid.UUID:
        return self._local_id

    @property
    def id(self) -> str:
        return self._id

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
            if handler.check(ctx, self):
                await handler.handle(ctx)

    async def send_message(self, text: str, channel_id: str, thread_id: str | None = None) -> None:
        await self.async_client.send_message(text, channel_id, thread_id)

    async def get_channels(self) -> list[dict[str, str]]:
        """
        Возвращает список каналов, в которых состоит бот, в формате:
        [{"_id": "channel_id", "t": "channel_type", "name": "channel_name"}, ...]
        """
        channels: list[dict[str, str]] = [
            {
                "_id": channel["_id"],
                "t": channel["t"],
                "name": "direct" if channel["t"] == RoomType.DIRECT else channel["name"]
            }
            for channel in await self.async_client.get_channels_raw()
        ]

        return channels

    def get_group_history(self, group_id: str, oldest: datetime = None, latest: datetime = None) -> dict[str, Any]:
        params = {
            "inclusive": True,
            "count": 0,
            "offset": 0
        }
        if oldest:
            params["oldest"] = oldest.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if latest:
            params["latest"] = latest.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        response = self.sync_client.groups_history(group_id, **params)
        if response.status_code != HTTPStatus.OK:
            return {}

        return response.json()
    
    def get_roles(self, user_id: str = None, username: str = None) -> list[str] | None:
        if not (user_id or username):
            return None
        
        response = self.sync_client.users_info(user_id=user_id, username=username)
        if response.status_code != HTTPStatus.OK:
            return None
        
        return response.json().get("user", {}).get("roles", [])

