from datetime import datetime
from models.dto import RequestContext
from dispatcher import Bot
from typing import Optional
from models.dto.stats_model import UserStats, ChannelStats, StatsData


class StatsService:
    async def collect_stats(
        self,
        bot: Bot,
        ctx: RequestContext,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> StatsData:
        users: dict[str, UserStats] = {}
        channels: dict[str, ChannelStats] = {}
        user_names: dict[str, str] = {}
        channel_names: dict[str, str] = {}

        raw_channels = await bot.get_channels()
        channel_names = {c["_id"]: c.get("name", "Unknown")
                         for c in raw_channels}

        for channel in raw_channels:
            channel_id = channel["_id"]

            if channel_id not in channels:
                channels[channel_id] = ChannelStats()

            history = bot.get_group_history(channel_id)
            for msg in history.get("messages", []):
                if "t" in msg:
                    continue

                user = msg["u"]
                user_id = user["_id"]

                if user_id not in user_names:
                    user_names[user_id] = user.get("username", "Unknown")

                if user_id not in users:
                    users[user_id] = UserStats()

                users[user_id].messages += 1
                channels[channel_id].messages += 1

                if "?" in msg.get("msg", ""):
                    users[user_id].questions += 1
                    channels[channel_id].questions += 1

                if "tmid" in msg:
                    users[user_id].answers += 1
                    channels[channel_id].answers += 1

        return StatsData(
            users=users,
            channels=channels,
            user_names=user_names,
            channel_names=channel_names
        )
