from __future__ import annotations

from collections.abc import Awaitable
from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING
from pydantic import BaseModel
import inspect


if TYPE_CHECKING:
    from dispatcher.bot import Bot
    from handler.filters import HandlerFilter
    from models.dto import RequestContext


type CallbackType[T:BaseModel] = Callable[[Bot, RequestContext, T], Awaitable[None]]


@dataclass
class Handler[T: BaseModel]:
    callback: CallbackType
    bot: Bot
    input_type: type[T]
    awaitable: bool = field(init=False)
    filters: list[HandlerFilter] = field(init=True, default_factory=list)

    def __post_init__(self) -> None:
        callback = inspect.unwrap(self.callback)
        self.awaitable = inspect.isawaitable(callback) or inspect.iscoroutinefunction(callback)

    async def handle(self, ctx: RequestContext) -> None:
        args = ctx.args if ctx.args is not None else {}
        input = self.input_type(**args)

        if self.awaitable:
            return await self.callback(self.bot, ctx, input)

        async def wrapper():
            self.callback(self.bot, ctx, input)

        await wrapper(self.bot, ctx, input)

    def check(self, ctx: RequestContext) -> bool:
        for filter in self.filters:
            if not filter.check(ctx):
                return False

        return True
