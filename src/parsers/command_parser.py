from abc import ABC, abstractmethod
from typing import Any, Type
from models.dto import RequestContext
from models.enums import Command
import argparse
from datetime import datetime
from enum import Enum


class CommandParserException(Exception):
    pass


class ArgShema:
    def __init__(self, type_: Type, required: bool = True, choices: list[Any] = None, default: Any = None, depends_on: list[str] = None, conflicts_with: list[str] = None) -> None:
        self.type = type_
        self.required = required
        self.default = default
        self.choices = choices or []
        self.depends_on = depends_on or []
        self.conflicts_with = conflicts_with or []


class CommandParser(ABC):
    @abstractmethod
    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        raise NotImplementedError


class ChatCommandParser(CommandParser):
    def __init__(self, commands_map: dict[str, Command], cmd_args_map: dict[Command, dict[str, ArgShema]], prefix: str = "!") -> None:
        self._prefix = prefix
        self._commands_map = {k.lower(): v for k, v in commands_map.items()}
        self._cmd_args_map = cmd_args_map

    def parse(self, ctx: RequestContext) -> tuple[Command | None, dict[str, Any] | None]:
        msg = ctx.msg.strip()
        if not msg.startswith(self._prefix):
            return None, None

        tokens = msg.split()

        command = self._extract_command(tokens[0])
        if command is None:
            return None, None
        
        if command not in self._cmd_args_map or not self._cmd_args_map[command]:
            return command, None
        
        try:
            args = self._extract_args(tokens[1:], self._cmd_args_map[command])
        except CommandParserException as e:
            raise e

        return command, args

    def _extract_command(self, token: str) -> Command:
        str_command = token[len(self._prefix):].lower()
        if str_command not in self._commands_map:
            return None, None

        return self._commands_map[str_command]

    def _extract_args(self, tokens: list[str], shema: dict[str, ArgShema]) -> dict[str, Any]:
        parser = argparse.ArgumentParser(prog="command", add_help=False)
        args_to_shema = {}
        
        for arg_name, arg_shema in shema.items():
            if arg_name == '__meta__':
                continue
            
            flag = f"--{arg_name}"
            kwargs = {'required': False, 'dest': arg_name}
            
            if arg_shema.choices:
                kwargs['choices'] = arg_shema.choices
            
            if arg_shema.type == bool:
                kwargs['action'] = 'store_true'
            else:
                kwargs['type'] = lambda val, t=arg_shema.type, n=arg_name: self._convert_type(val, t, n)
                
            if arg_shema.default is not None:
                kwargs['default'] = arg_shema.default
                
            parser.add_argument(flag, **kwargs)
            args_to_shema[arg_name] = arg_shema
            
        try:
            args_namespace, _ = parser.parse_known_args(tokens)
            args = vars(args_namespace)
        except SystemExit:
            raise CommandParserException("Невозможно распарсить аргументы команды")
            
        for arg_name, arg_val in args.items():
            arg_shema = args_to_shema[arg_name]
            if arg_val is None:
                continue
                
            for dep in arg_shema.depends_on:
                if not args.get(dep):
                    raise CommandParserException(f"Флаг --{arg_name} не может быть указан без флага --{dep}")
                    
            for conflict in arg_shema.conflicts_with:
                if args.get(conflict) is not None:
                    raise CommandParserException(f"Нельзя использовать флаг --{arg_name} с флагом --{conflict}")
                    
        for arg_name, arg_shema in args_to_shema.items():
            if arg_shema.required and args.get(arg_name) is None:
                raise CommandParserException(f"Обязателен флаг --{arg_name}")
                
        # meta = shema.get('__meta__', {})
        # for group in meta.get('one_required', []):
        #     print(f"Один из {group}", flush=True)
        #     values = [args.get(arg) for arg in group]
        #     present = [v for v in values if v is not None]
            
        #     if len(present) == 0:
        #         raise CommandParserException(f"Обязателен один из флагов: {' '.join(group)}")
        #     if len(present) > 1:
        #         raise CommandParserException(f"Можно использовать только один из флагов: {' '.join(group)}")
        
        return args
        
    def _convert_type(self, value: str, expected_type: type, arg_name: str) -> Any:
        if expected_type == datetime:
            try:
                date = datetime.strptime(value, "%d-%m-%Y")
                return date
            except ValueError:
                raise CommandParserException(f"Аргумент --{arg_name} должен иметь тип {expected_type.__name__} в формате дд-мм-гггг")
        elif issubclass(expected_type, Enum):
            try:
                print(f"Пробую определить тип {value}")
                return expected_type(value)
            except ValueError:
                raise CommandParserException(f'Аргумент --{arg_name} должен быть {expected_type.__name__}')
        try:
            return expected_type(value)
        except ValueError:
            raise CommandParserException(f"Аргумент --{arg_name} должен иметь тип {expected_type.__name__}")
