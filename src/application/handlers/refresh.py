from __future__ import annotations

from typing import TYPE_CHECKING
from models.domain import Channel
from models.dto import RequestContext, NoArgs
from application.handlers.interface import ApplicationHandler


if TYPE_CHECKING:
    from dispatcher.bot import Bot


class RefreshCommandHandler(ApplicationHandler):
    async def handle(self, bot: Bot, ctx: RequestContext, _: NoArgs) -> None:
        new_channels: list[Channel] = await bot.refresh_followed_channels()
        response_msg: str = "Нет новых каналов"

        if new_channels:
            response_blocks: list[str] = [f"- {channel.id} / {channel.name}" for channel in new_channels]
            response_msg = f"{len(new_channels)} новых канала(ов):\n<ID / Имя>\n{'\n'.join(response_blocks)}"

        await bot.send_message(
            response_msg,
            ctx.channel_id,
            ctx.thread_id,
        )
