from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.chat_message.chat_message_model import ChatMessage
from app.chat_message.chat_message_schema import ChatMessageCreate, ChatMessageUpdate
import logging

logger = logging.getLogger(__name__)


async def create_chat_message(db: AsyncSession, chat_message: ChatMessageCreate):
    db_chat_message = ChatMessage(**chat_message.dict())
    db.add(db_chat_message)
    await db.commit()
    await db.refresh(db_chat_message)
    return db_chat_message


async def get_chat_message(db: AsyncSession, chat_message_id: str):
    result = await db.execute(
        select(ChatMessage).filter(ChatMessage.id == chat_message_id)
    )
    return result.scalar_one_or_none()


async def get_chat_messages(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(ChatMessage).offset(skip).limit(limit))
    return result.scalars().all()


async def get_chat_messages_by_session(
    db: AsyncSession, session_id: str, skip: int = 0, limit: int = 100
):
    result = await db.execute(
        select(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_chat_message(
    db: AsyncSession, chat_message_id: str, chat_message: ChatMessageUpdate
):
    result = await db.execute(
        select(ChatMessage).filter(ChatMessage.id == chat_message_id)
    )
    db_chat_message = result.scalar_one_or_none()
    if db_chat_message:
        update_data = chat_message.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_chat_message, key, value)
        await db.commit()
        await db.refresh(db_chat_message)
    return db_chat_message


async def delete_chat_message(db: AsyncSession, chat_message_id: str):
    result = await db.execute(
        select(ChatMessage).filter(ChatMessage.id == chat_message_id)
    )
    db_chat_message = result.scalar_one_or_none()
    if db_chat_message:
        await db.delete(db_chat_message)
        await db.commit()
    return db_chat_message
