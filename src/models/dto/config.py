from pydantic import BaseModel
from datetime import datetime


class Config(BaseModel):
    # мб добавить ещё полезную инфу для других классов
    prefix: str | None = None
    server_url: str | None = None 