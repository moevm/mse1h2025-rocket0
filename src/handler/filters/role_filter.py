from handler.filters.interface import HandlerFilter
from models.dto import RequestContext
from dispatcher import Bot


class RoleFilter(HandlerFilter):
    def __init__(self, priviliged_roles: frozenset[str]) -> None:
        self._priviliged_roles = priviliged_roles

    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        user_roles = bot.get_roles(user_id=ctx.sender_id)
        return bool(self._priviliged_roles & set(user_roles))
