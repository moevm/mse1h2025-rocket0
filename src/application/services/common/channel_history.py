from datetime import datetime
from typing import Any
from dispatcher import Bot
from models.enums import RoomType


def get_channel_history(
    bot: Bot,
    channel: dict[str, str],
    oldest: datetime = None,
    latest: datetime = None,
) -> dict[str, Any]:
    match channel:
        case {"_id": id, "t": RoomType.CHANNEL}:
            return bot.get_channel_history(id, oldest, latest)
        case {"_id": id, "t": RoomType.GROUP}:
            return bot.get_group_history(id, oldest, latest)
        case _:
            return {}
