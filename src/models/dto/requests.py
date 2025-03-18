from pydantic import BaseModel
from typing import Any
from uuid import UUID
from models.enums import Command, EventType


class RequestContext(BaseModel):
    channel_id: str
    sender_id: str
    msg_id: str
    thread_id: str | None
    msg: str
    msg_qualifier: str | None
    unread: bool
    repeated: bool
    bot_local_id: UUID
    type: EventType
    cmd: Command | None = None
    args: dict[str, Any] | None = None
