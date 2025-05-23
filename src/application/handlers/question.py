from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext, NoArgs
from application.handlers.interface import ApplicationHandler
from logger_config import debug_logger

if TYPE_CHECKING:
    from dispatcher.bot import Bot


class QuestionHandler(ApplicationHandler):
    async def handle(self, bot: Bot, ctx: RequestContext, _: NoArgs) -> None:
        debug_logger.debug(ctx)

        await bot.send_message(
            f"Вы можете поискать свой ответ [тут](https://www.youtube.com/watch?v=dQw4w9WgXcQ).",
            ctx.channel_id,
            ctx.msg_id,
        )
