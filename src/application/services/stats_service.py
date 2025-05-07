import asyncio
from http import HTTPStatus
from datetime import datetime
from models.dto import RequestContext
from models.domain import UserStats, ChannelStats, StatsData
from application.services.common import get_channel_history
from dispatcher import Bot
from logger_config import general_logger
from typing import Any


class StatsService:
    def _get_single_user_roles_sync(self, bot: Bot, user_id: str) -> list[str] | None:
        """Synchronously fetches roles for a single user ID."""
        try:
            response = bot.sync_client.users_info(user_id=user_id)

            if response.status_code != HTTPStatus.OK:
                general_logger.warning(f"Failed to get info for user {user_id}: Status {response.status_code}")
                return None

            user_info: dict[str, Any] = response.json()
            if user_info.get("success") is False:
                general_logger.warning(f"API indicated failure for user {user_id}: {user_info.get('error', 'No error message')}")
                return None

            return user_info.get("user", {}).get("roles", [])
        except Exception as e:
            general_logger.error(f"Exception fetching roles for user {user_id}: {e}", exc_info=True)
            return None

    async def _fetch_user_roles(self, bot: Bot, user_ids: list[str]) -> dict[str, list[str]]:
        """Fetches roles for a list of user IDs concurrently."""
        user_roles_map: dict[str, list[str]] = {}

        async def _fetch_single_user_roles_async_wrapper(user_id: str) -> tuple[str, list[str] | None]:
            """Asynchronous wrapper to call the synchronous role fetching logic."""
            roles = await asyncio.to_thread(self._get_single_user_roles_sync, bot, user_id)
            return user_id, roles

        tasks = [_fetch_single_user_roles_async_wrapper(uid) for uid in user_ids]
        results = await asyncio.gather(*tasks)

        for user_id, roles in results:
            if roles is not None:
                user_roles_map[user_id] = roles

        return user_roles_map

    async def collect_stats(
        self,
        bot: Bot,
        ctx: RequestContext,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        all_channels: list[str] | None = None,
        all_users: list[str] | None = None,
        all_roles: list[str] | None = None
    ) -> StatsData:
        users: dict[str, UserStats] = {}
        channels: dict[str, ChannelStats] = {}
        user_names: dict[str, str] = {}
        channel_names: dict[str, str] = {}

        raw_channels = await bot.get_channels()
        channel_names = {c["_id"]: c.get("name", "Unknown")
                         for c in raw_channels}

        target_channels = raw_channels

        if all_channels:
            target_channels = [ch for ch in raw_channels if ch.get("name") in all_channels]
            channel_names = {c["_id"]: c.get("name", "Unknown") for c in target_channels}

        for channel in target_channels:
            channel_id = channel["_id"]

            if channel_id not in channels:
                channels[channel_id] = ChannelStats()

            history: dict[str, Any] = get_channel_history(bot, channel, from_date, to_date)
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

        final_users = users
        final_user_names = user_names

        collected_user_ids = list(final_user_names.keys())
        user_roles: dict[str, list[str]] = {}
        if collected_user_ids:
            user_roles = await self._fetch_user_roles(bot, collected_user_ids)

        target_user_ids: set[str] | None = None

        if all_users:
            user_ids_by_name = {uid for uid, name in user_names.items() if name in all_users}
            target_user_ids = user_ids_by_name

        if all_roles:
            role_list_lower = {r.lower() for r in all_roles}
            user_ids_by_role = {uid for uid, roles in user_roles.items() if any(role.lower() in role_list_lower for role in roles)}
            if target_user_ids is None:
                target_user_ids = user_ids_by_role
            else:
                target_user_ids.intersection_update(user_ids_by_role)

        if target_user_ids is not None:
            final_users = {uid: stats for uid, stats in users.items() if uid in target_user_ids}
            final_user_names = {uid: name for uid, name in user_names.items() if uid in target_user_ids}

            # Пересчитываем статистику каналов ТОЛЬКО для отфильтрованных пользователей
            final_channels: dict[str, ChannelStats] = {}
            for channel in target_channels:
                channel_id = channel["_id"]
                final_channels[channel_id] = ChannelStats()

                history = bot.get_group_history(channel_id, oldest=from_date, latest=to_date)
                for msg in history.get("messages", []):
                    if "t" in msg:
                        continue

                    msg_user_id = msg["u"]["_id"]
                    if msg_user_id in target_user_ids: 
                        final_channels[channel_id] = ChannelStats(
                            messages=final_channels[channel_id].messages + 1,
                            questions=final_channels[channel_id].questions +
                            (1 if "?" in msg.get("msg", "") else 0),
                            answers=final_channels[channel_id].answers +
                            (1 if "tmid" in msg else 0),
                            reactions=0
                        )
        else:
            final_channels = channels

        return StatsData(
            users=final_users,
            channels=final_channels,
            user_names=final_user_names,
            channel_names=channel_names,
            user_roles=user_roles
        )
