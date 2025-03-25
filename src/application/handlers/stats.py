from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext, StatsArgs
from models.domain import StatsData
from application.handlers.interface import ApplicationHandler
from application.services import StatsService

if TYPE_CHECKING:
    from dispatcher.bot import Bot


class StatsHandler(ApplicationHandler):
    def __init__(self, stats_service: StatsService) -> None:
        self._stats_service = stats_service

    async def handle(self, bot: "Bot", ctx: RequestContext, input: StatsArgs) -> None:
        stats = await self._stats_service.collect_stats(bot, ctx, input.from_date, input.to_date)
        response = self._format_response(stats)
        await bot.send_message(response, ctx.channel_id, ctx.thread_id)

    def _format_response(self, stats: StatsData) -> str:
        lines = ["Статистика пользователей:"]

        for user_id, data in stats.users.items():
            name = stats.user_names.get(user_id, "Unknown")
            lines.append(
                f"- {name}:\n"
                f"  Сообщений: {data.messages}\n"
                f"  Вопросов: {data.questions}\n"
                f"  Ответов: {data.answers}\n"
                f"  Реакций: {data.reactions_given} → / {data.reactions_received} ←"
            )

        lines.append("\nСтатистика по каналам:")
        for channel_id, data in stats.channels.items():
            name = stats.channel_names.get(channel_id, "Unknown")
            lines.append(
                f"- {name}:\n"
                f"  Сообщений: {data.messages}\n"
                f"  Вопросов: {data.questions}\n"
                f"  Ответов: {data.answers}\n"
                f"  Реакций: {data.reactions}"
            )

        return "\n".join(lines)
