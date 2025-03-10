from pydantic import BaseModel, Field
from datetime import datetime


class FindUnansweredArgs(BaseModel):
    from_date: datetime | None = Field(default=None, alias="from")
    to_date: datetime | None = Field(default=None, alias="to")
