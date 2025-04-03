from pydantic import BaseModel, Field
from datetime import datetime


class StatsArgs(BaseModel):
    from_date: datetime | None = Field(default=None, alias="from")
    to_date: datetime | None = Field(default=None, alias="to")
    channels: list[str] | None = None
