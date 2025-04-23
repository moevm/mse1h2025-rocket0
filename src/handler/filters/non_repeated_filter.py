from handler.filters.interface import HandlerFilter
from models.dto import RequestContext
from dispatcher import Bot


class NonRepeatedFilter(HandlerFilter):
    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        return not ctx.repeated
