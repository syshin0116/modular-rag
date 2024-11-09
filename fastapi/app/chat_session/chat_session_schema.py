from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ChatSessionBase(BaseModel):
    user_id: str
    context: Optional[Dict] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(ChatSessionBase):
    end_time: Optional[datetime] = None


class ChatSessionInDB(ChatSessionBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        orm_mode = True
