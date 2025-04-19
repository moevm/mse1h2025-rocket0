from __future__ import annotations

from pydantic import ValidationError
from typing import TYPE_CHECKING
from models.dto import RequestContext
from parsers import CommandParser, CommandParserException
from logger_config import requests_logger
import asyncio
import uuid

if TYPE_CHECKING:
    from dispatcher.bot import Bot


class Dispatcher:
    def __init__(self, bots: list[Bot], parser: CommandParser) -> None:
        self._bots: dict[uuid.UUID, Bot] = {bot.local_id: bot for bot in bots}
        self._parser: CommandParser = parser

        self._handling_tasks: set[asyncio.Task] = set()

    async def start_polling(self) -> None:
        polling_task: list[asyncio.Task] = []
        for _, bot in self._bots.items():
            polling_task.append(bot.run(self.dispatch))

        await asyncio.gather(*polling_task)

    def dispatch(self, *args) -> None:
        try:
            ctx = RequestContext(
                request_id=uuid.uuid4(),
                bot_local_id=args[0],
                type=args[1],
                channel_id=args[2],
                sender_id=args[3],
                msg_id=args[4],
                thread_id=args[5],
                msg=args[6],
                msg_qualifier=args[7],
                unread=args[8],
                repeated=args[9],
            )

        except ValidationError as e:
            requests_logger.error(f"Cannot parse request: {e}")
            return

        task = asyncio.create_task(self._process(ctx))
        self._handling_tasks.add(task)
        task.add_done_callback(self._handling_tasks.discard)

    async def _process(self, ctx: RequestContext) -> None:
        bot = self._bots[ctx.bot_local_id]

        if bot.id == ctx.sender_id:
            return

        requests_logger.info("Start handle request", extra=ctx.model_dump(by_alias=True))

        try:
            cmd, args = self._parser.parse(ctx)
        except CommandParserException as e:
            requests_logger.info(e, extra=ctx.model_dump(include={"request_id"}))
            return

        ctx.cmd, ctx.args = cmd, args

        # TODO: сделать исключения под, например, ошибку валидации и тут учитывать это, чтобы отличать
        # совсем критичные ошибки и просто какие-то предусмотренные нами
        try:
            await bot.resolve_handler(ctx)
        except Exception as e:
            requests_logger.error(f"Handle request error: {e}", extra=ctx.model_dump(include={"request_id"}))
            return

        requests_logger.info("Handle request successfully", extra=ctx.model_dump(include={"request_id"}))
