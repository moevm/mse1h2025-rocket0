from abc import ABC, abstractmethod
from typing import Any
from models.dto import RequestContext
from models.enums import Command


class CommandParser(ABC):
    @abstractmethod
    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        raise NotImplementedError


class ChatCommandParser(CommandParser):
    def __init__(self, commands_map: dict[str, Command], prefix: str = "!") -> None:
        self._prefix = prefix
        self._commands_map = {k.lower(): v for k, v in commands_map.items()}

    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        msg = ctx.msg.strip()
        if not msg.startswith(self._prefix):
            return None, None

        tokens = msg.split()

        command = self._extract_command(tokens[0])

        args = None
        if len(tokens) > 1:
            args = self._extract_args(tokens[1:])

        return command, args

    def _extract_command(self, token: str) -> Command:
        str_command = token[len(self._prefix):].lower()
        if str_command not in self._commands_map:
            return None, None

        return self._commands_map[str_command]

    def _extract_args(self, tokens: list[str]) -> dict[str, Any]:
        # TODO: Надо подумать, как извлекать аргументы, какие типы аргументов вообще хотим
        return {}
