from abc import abstractmethod, ABC
from models.dto import RequestContext
from dispatcher import Bot


class HandlerFilter(ABC):
    @abstractmethod
    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        raise NotImplementedError
