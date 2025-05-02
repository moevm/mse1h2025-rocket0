from datetime import datetime
from typing import Any
import re
from models.domain import ChatMessage, ChatMessageSender
from models.dto import RequestContext
from models.enums import RoomType
from dispatcher import Bot


class GroupService:
    def __init__(self, command_prefix, service_reactions, priviliged_roles):
        self._command_prefix = command_prefix
        self._service_reactions = service_reactions
        self._priviliged_roles = priviliged_roles

    async def get_unanswered_messages(
        self,
        bot: Bot,
        ctx: RequestContext,
        from_date: datetime = None,
        to_date: datetime = None,
    ) -> list[ChatMessage]:
        groups = list(filter(lambda chan: chan["t"] == RoomType.GROUP, await bot.get_channels()))
        result: list[ChatMessage] = []
        
        for group in groups:
            history_data: dict[str, Any] = bot.get_group_history(group["_id"], oldest=from_date, latest=to_date)
            messages: list[dict[str, Any]] = history_data.get("messages", [])

            unanswered: dict[str, ChatMessage] = {}
            answered: set[str] = set()

            for message in messages:
                message_id = message["_id"]
                if "t" in message:
                    continue

                if message["msg"].startswith(self._command_prefix):
                    continue

                sender_id = message["u"]["_id"]
                '''
                if sender_id == ctx.sender_id:
                    continue
                '''

                if sender_id == bot.id:
                    continue

                if "reactions" in message:
                    reactions = self._service_reactions & set(message["reactions"].keys())
                                
                    if any(
                        bool(self._priviliged_roles & set(bot.get_roles(username=username)))
                        for reaction in reactions
                        for username in message["reactions"][reaction]["usernames"]
                        ):
                        continue

                if "tmid" in message:
                    answered.add(message["tmid"])
                    unanswered.pop(message["tmid"], None)
                    continue

                if message_id not in answered:
                    unanswered[message_id] = ChatMessage(
                        id=message_id,
                        rid=message["rid"],
                        msg=message["msg"],
                        u=ChatMessageSender(id=sender_id, username=message["u"]["username"])
                    )

            result.extend(list(unanswered.values()))

        return result
    
    async def get_messages_by_pattern(
        self,
        bot: Bot,
        pattern: str
    ) -> list[ChatMessage]:
        regex = re.compile(pattern)
        groups = list(filter(lambda chan: chan["t"] == RoomType.GROUP, await bot.get_channels()))
        result: list[ChatMessage] = []
        
        for group in groups:
            history_data = bot.get_group_history(group["_id"])
            messages = history_data.get("messages", [])

            for message in messages:
                if "t" in message:
                    continue

                if message["msg"].startswith(self._command_prefix):
                    continue

                sender_id = message["u"]["_id"]

                if sender_id == bot.id:
                    continue
                
                if "msg" in message and regex.search(message["msg"]):
                    result.append(ChatMessage(
                        id=message["_id"],
                        rid=message["rid"],
                        msg=message["msg"],
                        u=ChatMessageSender(id=message["u"]["_id"], username=message["u"]["username"])
                    ))

        return result
