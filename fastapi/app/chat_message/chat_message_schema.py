from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class MessageSender(str, Enum):
    USER = "user"
    BOT = "bot"


class ChatMessageBase(BaseModel):
    session_id: str
    sender: MessageSender
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageUpdate(ChatMessageBase):
    content: str


class ChatMessageInDB(ChatMessageBase):
    id: str
    timestamp: datetime

    class Config:
        orm_mode = True
