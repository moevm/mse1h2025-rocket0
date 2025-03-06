from __future__ import annotations

from abc import abstractmethod, ABC
from pydantic import BaseModel
from typing import TYPE_CHECKING
from models.dto import RequestContext


if TYPE_CHECKING:
    from dispatcher.bot import Bot


class ApplicationHandler[T: BaseModel](ABC):
    @abstractmethod
    async def handle(self, bot: Bot, ctx: RequestContext, input: T) -> None:
        raise NotImplementedError
