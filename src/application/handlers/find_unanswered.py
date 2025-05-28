from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext, FindUnansweredArgs
from application.handlers.interface import ApplicationHandler
from application.services import ChannelService


if TYPE_CHECKING:
    from dispatcher.bot import Bot


class FindUnansweredHandler(ApplicationHandler):
    def __init__(self, server_url: str, channel_service: ChannelService) -> None:
        self._server_url: str = server_url
        self._group_service: ChannelService = channel_service

    async def handle(self, bot: Bot, ctx: RequestContext, input: FindUnansweredArgs) -> None:
        messages = await self._group_service.get_unanswered_messages(bot, ctx, input.from_date, input.to_date, input.hours)

        response_blocks: list[str] = [
            f"[ ]({bot.http}://{self._server_url}/group/{message.rid}?msg={message.id})\n"
            for message in messages
        ]

        if len(response_blocks) == 0:
            await bot.send_message("Неотвеченных сообщений не найдено", ctx.channel_id, ctx.thread_id)
            return

        await bot.send_message(
            f'{"".join(response_blocks)}\nКоличество неотвеченных сообщений: {len(response_blocks)}',
            ctx.channel_id,
            ctx.thread_id
        )
