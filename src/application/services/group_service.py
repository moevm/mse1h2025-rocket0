from datetime import datetime
from typing import Any
from models.domain import ChatMessage, ChatMessageSender
from models.dto import RequestContext
from dispatcher import Bot


GROUP_TYPE = "p"


class GroupService:
    async def get_unanswered_messages(
        self,
        bot: Bot,
        ctx: RequestContext,
        from_date: datetime = None,
        to_date: datetime = None
    ) -> list[ChatMessage]:
        groups = list(filter(lambda chan: chan["t"] == GROUP_TYPE, await bot.get_channels()))
        result: list[ChatMessage] = []

        for group in groups:
            # TODO: oldest и latest аргументы заюзать
            history_data: dict[str, Any] = bot.get_group_history(group["_id"])
            messages: list[dict[str, Any]] = history_data.get("messages", [])

            unanswered: dict[str, ChatMessage] = {}
            answered: set[str] = set()

            for message in messages:
                message_id = message["_id"]
                if "t" in message:
                    continue

                sender_id = message["u"]["_id"]
                '''
                if sender_id == ctx.sender_id:
                    continue
                '''

                if sender_id == bot.id:
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
