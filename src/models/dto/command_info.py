from dataclasses import dataclass
from models.enums import Command
from models.dto import ArgSchema


@dataclass
class CommandInfo:
    cmd: Command
    schema: dict[str, ArgSchema] | None = None