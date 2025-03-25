from handler.filters.interface import HandlerFilter
from models.dto import RequestContext


class NonRepeatedFilter(HandlerFilter):
    def check(self, ctx: RequestContext) -> bool:
        return not ctx.repeated
