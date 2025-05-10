from pydantic import BaseModel


class FindMessageArgs(BaseModel):
    pattern: str 