from pydantic import BaseModel
from datetime import datetime


class FindUnansweredArgs(BaseModel):
    from_date: datetime | None = None
    to_date: datetime | None = None
