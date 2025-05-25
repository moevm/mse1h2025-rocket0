from pydantic import BaseModel, Field
from datetime import datetime


class StatsArgs(BaseModel):
    from_date: datetime | None = Field(default=None, alias="from")
    to_date: datetime | None = Field(default=None, alias="to")
    hours: int | None = None
    channels: list[str] | None = None
    users: list[str] | None = None
    roles: list[str] | None = None
    