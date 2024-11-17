from sqlalchemy import Column, ForeignKey, DateTime, JSON, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.model_base import Base
from uuid import uuid4


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    is_kakao = Column(Boolean, nullable=False, default=False)  # 카카오톡 여부
    context = Column(JSON, nullable=True)  # 세션에 대한 요약/기억 정보
    start_time = Column(DateTime(timezone=True), server_default=func.now())
