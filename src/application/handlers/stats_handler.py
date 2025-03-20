from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext
from models.dto.stats_args import StatsArgs
from application.handlers.interface import ApplicationHandler
from application.services.stats_service import StatsService

if TYPE_CHECKING:
    from dispatcher.bot import Bot


class StatsHandler(ApplicationHandler):
    def __init__(self, stats_service: StatsService) -> None:
        self._stats_service: StatsService = stats_service

    async def handle(self, bot: Bot, ctx: RequestContext, input: StatsArgs) -> None:
        stats = await self._stats_service.collect_stats(bot, ctx, input.from_date, input.to_date)
        await bot.send_message(stats, ctx.channel_id, ctx.thread_id)
