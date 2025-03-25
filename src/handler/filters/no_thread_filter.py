from handler.filters.interface import HandlerFilter
from models.dto import RequestContext


class NoThreadFilter(HandlerFilter):
    def check(self, ctx: RequestContext) -> bool:
        return ctx.thread_id is None
