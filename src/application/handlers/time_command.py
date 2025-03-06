from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from models.dto import RequestContext, NoArgs
from application.handlers.interface import ApplicationHandler


if TYPE_CHECKING:
    from dispatcher.bot import Bot


class TimeCommandHandler(ApplicationHandler):
    async def handle(self, bot: Bot, ctx: RequestContext, _: NoArgs) -> None:
        await bot.send_message(
            f"Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ctx.channel_id,
            ctx.thread_id,
        )
