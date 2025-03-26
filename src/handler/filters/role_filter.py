from handler.filters.interface import HandlerFilter
from models.dto import RequestContext
from dispatcher import Bot
from pprint import pprint


class RoleFilter(HandlerFilter):
    def __init__(self, roles: tuple[str]) -> None:
        self._roles = roles

    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        response = bot.sync_client.users_info(user_id=ctx.sender_id)
        if response.status_code != 200:
             return False
        
        user_roles = response.json().get("user", {}).get("roles", [])
        return bool(set(self._roles) & set(user_roles))
