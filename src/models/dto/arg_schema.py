from dataclasses import dataclass
from typing import Any, Type, Optional


@dataclass
class ArgSchema:
    type: Type
    required: bool = False
    default: Any = None
    nargs: Optional[str] = None
