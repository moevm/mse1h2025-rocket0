from dataclasses import dataclass


@dataclass
class ChatMessageSender:
    id: str
    username: str

 
@dataclass
class ChatMessage:
    id: str
    rid: str
    msg: str
    u: ChatMessageSender
