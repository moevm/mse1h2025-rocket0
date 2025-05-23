from datetime import datetime
from typing import Any
from dispatcher import Bot
from models.domain import Channel
from models.enums import RoomType


def get_channel_history(
    bot: Bot,
    channel: Channel,
    oldest: datetime = None,
    latest: datetime = None,
) -> dict[str, Any]:
     match channel.type:
        case RoomType.CHANNEL:
            return bot.get_channel_history(channel.id, oldest, latest)
        case RoomType.GROUP:
            return bot.get_group_history(channel.id, oldest, latest)
        case _:
            return {}
