from datetime import datetime


from models.dto import RequestContext
from dispatcher import Bot

from typing import Dict


class StatsService:
    async def collect_stats(
        self,
        bot: Bot,
        ctx: RequestContext,
        from_date: datetime = None,
        to_date: datetime = None
    ) -> str:

        user_stats: Dict[str, Dict[str, int]] = {}
        channel_stats: Dict[str, Dict[str, int]] = {}

        channels = await bot.get_channels()
        channel_info = {channel["_id"]: channel.get(
            "name", "Unknown") for channel in channels}

        user_info = {}
        for channel in channels:
            history_data = bot.get_group_history(channel["_id"])
            messages = history_data.get("messages", [])
            for msg in messages:
                if "u" in msg:
                    user_id = msg["u"]["_id"]
                    if user_id not in user_info:
                        user_info[user_id] = msg["u"].get(
                            "username", "Unknown")

        for channel in channels:
            channel_id = channel["_id"]

            history_data = bot.get_group_history(channel_id)
            messages = history_data.get("messages", [])

            for msg in messages:

                if "t" in msg:
                    continue

                sender_id = msg["u"]["_id"]

                if sender_id not in user_stats:
                    user_stats[sender_id] = {
                        "messages": 0,
                        "questions": 0,
                        "answers": 0,
                        "reactions_given": 0,
                        "reactions_received": 0,
                    }

                user_stats[sender_id]["messages"] += 1

                if "?" in msg.get("msg", ""):
                    user_stats[sender_id]["questions"] += 1

                if "tmid" in msg:
                    user_stats[sender_id]["answers"] += 1

                if channel_id not in channel_stats:
                    channel_stats[channel_id] = {
                        "messages": 0,
                        "questions": 0,
                        "answers": 0,
                        "reactions": 0,
                    }
                channel_stats[channel_id]["messages"] += 1
                if "?" in msg.get("msg", ""):
                    channel_stats[channel_id]["questions"] += 1
                if "tmid" in msg:
                    channel_stats[channel_id]["answers"] += 1

        message = "Статистика пользователей:\n"
        for user_id, stats in user_stats.items():
            username = user_info.get(user_id, "Unknown")
            message += (
                f"- Пользователь {username} ({user_id}):\n"
                f"  Сообщений: {stats['messages']}\n"
                f"  Вопросов: {stats['questions']}\n"
                f"  Ответов: {stats['answers']}\n"
                f"  Поставлено реакций: {stats['reactions_given']}\n"
                f"  Получено реакций: {stats['reactions_received']}\n"
            )

        message += "\nСтатистика по каналам:\n"
        for channel_id, stats in channel_stats.items():
            channel_name = channel_info.get(channel_id, "Unknown")
            message += (
                f"- Канал {channel_name} ({channel_id}):\n"
                f"  Сообщений: {stats['messages']}\n"
                f"  Вопросов: {stats['questions']}\n"
                f"  Ответов: {stats['answers']}\n"
                f"  Реакций: {stats['reactions']}\n"
            )

        return message
