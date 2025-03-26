from handler.filters.interface import HandlerFilter
from models.dto import RequestContext
from models.enums import Command
from dispatcher import Bot


class CommandFilter(HandlerFilter):
    def __init__(self, cmd: Command) -> None:
        self._cmd = cmd

    def check(self, ctx: RequestContext, bot: Bot) -> bool:
        if ctx.cmd is not None and ctx.cmd == self._cmd:
            return True

        return False
