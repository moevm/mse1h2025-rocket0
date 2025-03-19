from abc import ABC, abstractmethod
from typing import Any
from models.dto import RequestContext
from models.enums import Command
import argparse
from datetime import datetime


class CommandParser(ABC):
    @abstractmethod
    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        raise NotImplementedError


class ChatCommandParser(CommandParser):
    def __init__(self, commands_map: dict[str, Command], prefix: str = "!") -> None:
        self._prefix = prefix
        self._commands_map = {k.lower(): v for k, v in commands_map.items()}
        self._arg_parsers = self._make_parsers()

    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        msg = ctx.msg.strip()
        if not msg.startswith(self._prefix):
            return None, None

        tokens = msg.split()

        command = self._extract_command(tokens[0])
        if command is None:
            return None, None

        args = self._extract_args(command, tokens[1:])

        return command, args
    
    def _make_parsers(self) -> dict[Command, argparse.ArgumentParser]:
        parsers = {}
        
        def parse_date(str_date: str) -> datetime:
            try:
                date = datetime.strptime(str_date, "%d-%m-%Y")
                return date
            except ValueError:
                raise argparse.ArgumentTypeError(f"Дата должна быть записана в формате: дд-мм-гггг")
        
        find_unanswered_parser = argparse.ArgumentParser(prog="!find_unanswered", add_help=False)
        find_unanswered_parser_group = find_unanswered_parser.add_mutually_exclusive_group(required=True)
        find_unanswered_parser_group.add_argument("-h", "--hours", type=int, help="Период в часах, за который вести поиск")
        find_unanswered_parser_group.add_argument("-f", "--from", dest="from_date", type=parse_date, help="Дата, с которой ведётся поиск в формате: дд-мм-гггг")
        find_unanswered_parser.add_argument("-t", "--to", dest="to_date", type=parse_date, help="Дата, до которой ведётся поиск включительно в формате: дд-мм-гггг (можно не указывать, тогда поиск будет вестись до текущего времени)")
        find_unanswered_parser.add_argument("-s", "--short", action="store_true", help="Краткий вывод: только названия каналов и кол-во непрочитанных сообщений в них")
        
        parsers[self._commands_map["find_unanswered"]] = find_unanswered_parser
        
        return parsers

    def _extract_command(self, token: str) -> Command:
        str_command = token[len(self._prefix):].lower()
        if str_command not in self._commands_map:
            return None, None

        return self._commands_map[str_command]

    def _extract_args(self, command:Command, tokens: list[str]) -> dict[str, Any]:
        if command not in self._arg_parsers:
            #{} или None возвращать?
            return {}
        
        parser = self._arg_parsers[command]
        try:
            parsed_args = parser.parse_args(tokens)
            args =  vars(parsed_args)
            
            if args.get("to_date") and not args.get("from_date"):
                return {"error": "Флаг --to/-t нельзя использовать без --from/-f"}
            
            if args.get("from_date") and args.get("to_date"):
                if args["from_date"] > args["to_date"]:
                    return {"error": "Начальная дата не может быть позже конечной"}
            
            return args
        except SystemExit:
            return {"error": "Неверные аргументы"}
