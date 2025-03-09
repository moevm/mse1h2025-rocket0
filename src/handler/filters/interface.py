from abc import abstractmethod, ABC
from models.dto import RequestContext


class HandlerFilter(ABC):
    @abstractmethod
    def check(self, ctx: RequestContext) -> bool:
        raise NotImplementedError
