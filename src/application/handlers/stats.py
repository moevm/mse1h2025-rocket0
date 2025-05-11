from __future__ import annotations

from typing import TYPE_CHECKING
from models.dto import RequestContext, StatsArgs
from models.domain import StatsData, UserStats
from application.handlers.interface import ApplicationHandler
from application.services import StatsService
import csv
import io
import tempfile
import os

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
        csv_content = self._create_csv_content(stats)

        with tempfile.NamedTemporaryFile(mode='w+', suffix=".csv", delete=False, encoding='utf-8') as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            await bot.send_file(
                channel_id=ctx.channel_id,
                file=temp_file_path,
            )

            await bot.send_message(
                text=f"Statistics for period from {input.from_date} to {input.to_date}",
                channel_id=ctx.channel_id,
                thread_id=ctx.thread_id
            )
        finally:
            os.remove(temp_file_path)

    def _create_csv_content(self, stats: StatsData) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["User statistics"])
        writer.writerow([
            "Username", "Messages", "Questions", "Answers",
            "Reactions given", "Reactions received", "Roles"
        ])
        for user_id, data in stats.users.items():
            name = stats.user_names.get(user_id, "Unknown")
            roles = ", ".join(stats.user_roles.get(user_id, []))
            writer.writerow([
                name, data.messages, data.questions, data.answers,
                data.reactions_given, data.reactions_received, roles
            ])

        writer.writerow([])

        writer.writerow(["Channel statistics"])
        writer.writerow([
            "Channel name", "Messages", "Questions", "Answers", "Reactions"
        ])
        for channel_id, data in stats.channels.items():
            name = stats.channel_names.get(channel_id, "Unknown")
            writer.writerow([
                name, data.messages, data.questions, data.answers, data.reactions
            ])

        writer.writerow([])

        role_stats: dict[str, UserStats] = {}
        for user_id, user_stat in stats.users.items():
            roles = stats.user_roles.get(user_id, [])
            for role in roles:
                if role not in role_stats:
                    role_stats[role] = UserStats()
                role_stats[role] = UserStats(
                    messages=role_stats[role].messages + user_stat.messages,
                    questions=role_stats[role].questions + user_stat.questions,
                    answers=role_stats[role].answers + user_stat.answers,
                    reactions_given=role_stats[role].reactions_given +
                    user_stat.reactions_given,
                    reactions_received=role_stats[role].reactions_received +
                    user_stat.reactions_received
                )

        if role_stats:
            writer.writerow(["Role statistics"])
            writer.writerow([
                "Role", "Messages", "Questions", "Answers",
                "Reactions given", "Reactions received"
            ])
            for role, data in role_stats.items():
                writer.writerow([
                    role, data.messages, data.questions, data.answers,
                    data.reactions_given, data.reactions_received
                ])

        return output.getvalue()
