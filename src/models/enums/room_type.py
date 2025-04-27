from enum import Enum


class RoomType(str, Enum):
    GROUP = "p"
    CHANNEL = "c"
    DIRECT = "d"
