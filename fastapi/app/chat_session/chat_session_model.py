from sqlalchemy import Column, ForeignKey, DateTime, JSON, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.model_base import Base
from uuid import uuid4


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    context = Column(JSON)
