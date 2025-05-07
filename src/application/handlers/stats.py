from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext, StatsArgs
from models.domain import StatsData, UserStats
from application.handlers.interface import ApplicationHandler
from application.services import StatsService

if TYPE_CHECKING:
    from dispatcher.bot import Bot


class StatsHandler(ApplicationHandler):
    def __init__(self, stats_service: StatsService) -> None:
        self._stats_service = stats_service

    async def handle(self, bot: "Bot", ctx: RequestContext, input: StatsArgs) -> None:
        stats = await self._stats_service.collect_stats(
            bot,
            ctx,
            input.from_date,
            input.to_date,
            input.channels,
            input.users,
            input.roles
        )
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

        # Агрегация статистики по ролям
        role_stats: dict[str, UserStats] = {}
        for user_id, user_stat in stats.users.items():
            roles = stats.user_roles.get(user_id, [])
            for role in roles:
                if role not in role_stats:
                    role_stats[role] = UserStats()
                # Суммируем статистику для каждой роли
                role_stats[role] = UserStats(
                    messages=role_stats[role].messages + user_stat.messages,
                    questions=role_stats[role].questions + user_stat.questions,
                    answers=role_stats[role].answers + user_stat.answers,
                    reactions_given=role_stats[role].reactions_given + user_stat.reactions_given,
                    reactions_received=role_stats[role].reactions_received + user_stat.reactions_received
                )
        
        # Добавляем блок статистики по ролям
        if role_stats:
            lines.append("\nСтатистика по ролям:")
            for role, data in role_stats.items():
                lines.append(
                    f"- {role}:\n"
                    f"  Сообщений: {data.messages}\n"
                    f"  Вопросов: {data.questions}\n"
                    f"  Ответов: {data.answers}\n"
                    f"  Реакций выдано: {data.reactions_given}\n"
                    f"  Реакций получено: {data.reactions_received}"
                )

        return "\n".join(lines)
