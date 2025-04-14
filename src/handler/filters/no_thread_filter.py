from handler.filters.interface import HandlerFilter
from models.dto import RequestContext
from dispatcher import Bot


class NoThreadFilter(HandlerFilter):
    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        return ctx.thread_id is None
