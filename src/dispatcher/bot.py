from __future__ import annotations

from rocketchat_async import RocketChat as RocketChatAsync
from rocketchat_API.rocketchat import RocketChat
from typing import Callable, Any, TYPE_CHECKING
from functools import partial
from http import HTTPStatus
from pydantic import BaseModel
from models.enums import EventType
from handler import Handler, CallbackType
import asyncio
import uuid
from logger_config import general_logger


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
            if handler.check(ctx):
                await handler.handle(ctx)

    async def send_message(self, text: str, channel_id: str, thread_id: str | None = None) -> None:
        await self.async_client.send_message(text, channel_id, thread_id)

    async def get_channels(self) -> list[dict[str, str]]:
        """
        Возвращает список каналов, в которых состоит бот, в формате:
        [{"_id": "channel_id", "name": "channel_name", "t": "channel_type"}, ...]
        """
        channel_list = [
            {"_id": channel["_id"], "name": channel["name"], "t": channel["t"]}
            for channel in await self.async_client.get_channels_raw()
        ]

        return channel_list

    # TODO: тут тоже надо будет поддержать oldest и latest (думаю надо будет уже str передавать, но мб и datetime)
    def get_group_history(self, group_id: str) -> dict[str, Any]:
        response = self.sync_client.groups_history(group_id, inclusive=True, count=10000000)
        if response.status_code != HTTPStatus.OK:
            return {}

        return response.json()

    async def get_user_roles(self, user_ids: list[str]) -> dict[str, list[str]]:
        user_roles_map: dict[str, list[str]] = {}

        async def _fetch_single_user_roles(user_id: str) -> tuple[str, list[str] | None]:
            try:
                response = await asyncio.to_thread(
                    self.sync_client.users_info, user_id=user_id
                )
                response.raise_for_status()
                user_info = response.json()
                if user_info.get("success"):
                    roles = user_info.get("user", {}).get("roles", [])
                    return user_id, roles
                else:
                    general_logger.warning(f"Failed to get info for user {user_id}: {user_info.get('error')}")
                    return user_id, None
            except Exception as e:
                general_logger.error(f"Error fetching roles for user {user_id}: {e}")
                return user_id, None

        tasks = [_fetch_single_user_roles(uid) for uid in user_ids]
        results = await asyncio.gather(*tasks)

        for user_id, roles in results:
            if roles is not None:
                user_roles_map[user_id] = roles
        
        return user_roles_map
