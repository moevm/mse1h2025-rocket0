import re

from handler.filters.interface import HandlerFilter
from models.dto import RequestContext
from dispatcher import Bot


class RegexFilter(HandlerFilter):
    def __init__(self, expression: str | re.Pattern[str]) -> None:
        self._expression = re.compile(expression) if isinstance(expression, str) else expression

    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        return bool(re.fullmatch(self._expression, ctx.msg))
