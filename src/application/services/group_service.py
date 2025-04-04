from datetime import datetime, timezone
from typing import Any
from models.domain import ChatMessage, ChatMessageSender
from models.dto import RequestContext
from dispatcher import Bot


GROUP_TYPE = "p"


class GroupService:
    def __init__(self, command_prefix):
        self._command_prefix = command_prefix

    async def get_unanswered_messages(
        self,
        bot: Bot,
        ctx: RequestContext,
    ) -> list[ChatMessage]:
        groups = list(filter(lambda chan: chan["t"] == GROUP_TYPE, await bot.get_channels()))
        result: list[ChatMessage] = []
        #TODO: разобраться с таймзонами (даты верные, часы опаздывают от тех, что в чате)
        if ctx.args.get('from') is None:
            min_ts = None
            for group in groups:
                history_data: dict[str, Any] = bot.get_group_history(group["_id"])
                messages = history_data.get("messages", [])
                for message in messages:
                    msg_ts = datetime.fromisoformat(message.get("ts"))
                    if min_ts is None or msg_ts < min_ts:
                            min_ts = msg_ts
            effective_from_date = min_ts or datetime.now(timezone.utc)
        else:
            effective_from_date = ctx.args.get('from').astimezone(timezone.utc)
        effective_to_date = ctx.args.get('to').astimezone(timezone.utc) if ctx.args.get('to') is not None else datetime.now(timezone.utc)
        

        for group in groups:
            # TODO: oldest и latest аргументы заюзать
            history_data: dict[str, Any] = bot.get_group_history(group["_id"])
            messages: list[dict[str, Any]] = history_data.get("messages", [])

            unanswered: dict[str, ChatMessage] = {}
            answered: set[str] = set()

            for message in messages:
                
                msg_ts = datetime.fromisoformat(message.get("ts"))
                if msg_ts and not (effective_from_date <= msg_ts <= effective_to_date):
                    continue
                
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
