from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.chat_session.chat_session_model import ChatSession
from app.chat_session.chat_session_schema import ChatSessionCreate, ChatSessionUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def create_chat_session(db: AsyncSession, chat_session: ChatSessionCreate):
    db_chat_session = ChatSession(**chat_session.dict())
    db.add(db_chat_session)
    await db.commit()
    await db.refresh(db_chat_session)
    return db_chat_session


async def get_chat_session(db: AsyncSession, chat_session_id: str):
    result = await db.execute(
        select(ChatSession).filter(ChatSession.id == chat_session_id)
    )
    return result.scalar_one_or_none()


async def get_chat_sessions(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(ChatSession).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_chat_sessions(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100
):
    result = await db.execute(
        select(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_chat_session(
    db: AsyncSession, chat_session_id: str, chat_session: ChatSessionUpdate
):
    result = await db.execute(
        select(ChatSession).filter(ChatSession.id == chat_session_id)
    )
    db_chat_session = result.scalar_one_or_none()
    if db_chat_session:
        update_data = chat_session.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_chat_session, key, value)
        await db.commit()
        await db.refresh(db_chat_session)
    return db_chat_session


async def delete_chat_session(db: AsyncSession, chat_session_id: str):
    result = await db.execute(
        select(ChatSession).filter(ChatSession.id == chat_session_id)
    )
    db_chat_session = result.scalar_one_or_none()
    if db_chat_session:
        await db.delete(db_chat_session)
        await db.commit()
    return db_chat_session
