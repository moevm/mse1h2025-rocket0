from abc import ABC, abstractmethod
from typing import Any
from models.dto import RequestContext
from models.enums import Command
from dataclasses import dataclass
import argparse
from datetime import datetime


@dataclass
class ArgSchema[T]:
    type: type[T]
    required: bool = False
    default: T | None = None
    nargs: str | None = None
    positional: bool = False


@dataclass
class CommandInfo:
    cmd: Command
    schema: dict[str, ArgSchema] | None = None


class CommandParserException(Exception):
    pass


class CommandParser(ABC):
    @abstractmethod
    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        raise NotImplementedError


class ChatCommandParser(CommandParser):
    def __init__(self, commands_map: dict[str, CommandInfo], prefix: str = "!") -> None:
        self._prefix = prefix
        self._commands_map = {k.lower(): v for k, v in commands_map.items()}

    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        msg = ctx.msg.strip()
        if not msg.startswith(self._prefix):
            return None, None

        tokens = msg.split()

        str_command = tokens[0][len(self._prefix):].lower()

        command = self._extract_command(str_command)
        if command is None:
            return None, None

        if not self._commands_map[str_command].schema:
            return command, None

        args = self._extract_args(tokens[1:], self._commands_map[str_command].schema)

        return command, args

    def _extract_command(self, str_command: str) -> Command:
        if str_command not in self._commands_map:
            return None

        return self._commands_map[str_command].cmd

    def _extract_args(self, tokens: list[str], sсhema: dict[str, ArgSchema]) -> dict[str, Any]:
        parser = argparse.ArgumentParser(prog="command", add_help=False)

        for arg_name, arg_sсhema in sсhema.items():
            kwargs = {}
            if arg_sсhema.positional:
                flag = arg_name
            else:
                flag = f"--{arg_name}"
                kwargs['dest'] = arg_name

            if arg_sсhema.type == bool:
                kwargs['action'] = 'store_true'
            else:
                kwargs['type'] = lambda val, t=arg_sсhema.type, n=arg_name: self._convert_type(val, t, n)

            if arg_sсhema.default is not None:
                kwargs['default'] = arg_sсhema.default

            if arg_sсhema.required:
                kwargs['required'] = True

            if arg_sсhema.nargs is not None:
                kwargs['nargs'] = arg_sсhema.nargs

            parser.add_argument(flag, **kwargs)

        try:
            args_namespace, _ = parser.parse_known_args(tokens)
            args = vars(args_namespace)
        except SystemExit:
            raise CommandParserException("Cannot parse command arguments")

        return args

    def _convert_type(self, value: str, expected_type: type, arg_name: str) -> Any:
        try:
            if expected_type == datetime:
                date = datetime.fromisoformat(value)
                return date
            return expected_type(value)
        except ValueError:
            raise CommandParserException(f"Arg `--{arg_name}` must be type of `{expected_type.__name__}`")
