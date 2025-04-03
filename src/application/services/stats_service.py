from datetime import datetime
from models.dto import RequestContext
from models.domain import UserStats, ChannelStats, StatsData
from dispatcher import Bot


class StatsService:
    async def collect_stats(
        self,
        bot: Bot,
        ctx: RequestContext,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        channel_list: list[str] | None = None
    ) -> StatsData:
        users: dict[str, UserStats] = {}
        channels: dict[str, ChannelStats] = {}
        user_names: dict[str, str] = {}
        channel_names: dict[str, str] = {}

        raw_channels = await bot.get_channels()
        channel_names = {c["_id"]: c.get("name", "Unknown")
                         for c in raw_channels}

        target_channels = raw_channels

        if channel_list:
            target_channels = [ch for ch in raw_channels if ch.get("name") in channel_list]
            channel_names = {c["_id"]: c.get("name", "Unknown") for c in target_channels}

        for channel in target_channels:
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

                users[user_id] = UserStats(
                    messages=users[user_id].messages + 1,
                    questions=users[user_id].questions +
                    (1 if "?" in msg.get("msg", "") else 0),
                    answers=users[user_id].answers +
                    (1 if "tmid" in msg else 0),
                    reactions_given=users[user_id].reactions_given,
                    reactions_received=users[user_id].reactions_received
                )

                channels[channel_id] = ChannelStats(
                    messages=channels[channel_id].messages + 1,
                    questions=channels[channel_id].questions +
                    (1 if "?" in msg.get("msg", "") else 0),
                    answers=channels[channel_id].answers +
                    (1 if "tmid" in msg else 0),
                    reactions=channels[channel_id].reactions
                )

        return StatsData(
            users=users,
            channels=channels,
            user_names=user_names,
            channel_names=channel_names
        )
