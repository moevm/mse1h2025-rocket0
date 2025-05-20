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
            f"Пока вы ждёте ответ попробуйте поискать ответ на ваш вопрос [тут](https://se.moevm.info/doku.php/start).",
            ctx.channel_id,
            ctx.msg_id,
        )
