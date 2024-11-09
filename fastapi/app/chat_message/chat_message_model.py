from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Relationship
from app.db.model_base import Base
import enum
from uuid import uuid4


class MessageSender(str, enum.Enum):
    USER = "user"
    BOT = "bot"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    sender = Column(Enum(MessageSender), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
