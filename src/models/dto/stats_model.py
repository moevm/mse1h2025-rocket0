from pydantic import BaseModel


class UserStats(BaseModel):
    messages: int = 0
    questions: int = 0
    answers: int = 0
    reactions_given: int = 0
    reactions_received: int = 0


class ChannelStats(BaseModel):
    messages: int = 0
    questions: int = 0
    answers: int = 0
    reactions: int = 0


class StatsData(BaseModel):
    users: dict[str, UserStats]
    channels: dict[str, ChannelStats]
    user_names: dict[str, str]
    channel_names: dict[str, str]
