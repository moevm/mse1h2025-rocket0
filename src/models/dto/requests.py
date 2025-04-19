from pydantic import BaseModel, Field
from typing import Any
from uuid import UUID
from models.enums import Command, EventType


class RequestContext(BaseModel):
    request_id: UUID
    channel_id: str
    sender_id: str
    msg_id: str
    thread_id: str | None = None
    msg: str = Field(serialization_alias="req_msg")
    msg_qualifier: str | None = None
    unread: bool
    repeated: bool
    bot_local_id: UUID
    type: EventType
    cmd: Command | None = None
    args: dict[str, Any] | None = Field(None, serialization_alias="req_args")
