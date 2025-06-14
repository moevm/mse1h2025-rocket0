from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext, FindMessageArgs
from application.handlers.interface import ApplicationHandler
from application.services import ChannelService


if TYPE_CHECKING:
    from dispatcher.bot import Bot


class FindMessageHandler(ApplicationHandler):
    def __init__(self, server_url: str, channel_service: ChannelService) -> None:
        self._server_url = server_url
        self._channel_service = channel_service

    async def handle(self, bot: Bot, ctx: RequestContext, input: FindMessageArgs) -> None:
        messages = await self._channel_service.get_messages_by_pattern(bot, input.pattern)

        response_blocks: list[str] = [
            f"[ ]({bot.http}://{self._server_url}/group/{message.rid}?msg={message.id})\n"
            for message in messages
        ]

        if len(response_blocks) == 0:
            await bot.send_message("Сообщений, удовлетворяющих паттерну, не найдено", ctx.channel_id, ctx.msg_id)
            return

        await bot.send_message(
            f'{"".join(response_blocks)}\nНайдено сообщений: {len(response_blocks)}',
            ctx.channel_id,
            ctx.msg_id,
        )
