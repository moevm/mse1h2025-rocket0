from dataclasses import dataclass
from typing import TypeVar, Generic


T = TypeVar("T")

@dataclass
class ArgSchema(Generic[T]):
    type: type[T]
    required: bool = False
    default: T | None = None
    nargs: str | None = None
