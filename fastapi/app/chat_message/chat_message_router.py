from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.chat_message.chat_message_crud import (
    create_chat_message,
    get_chat_message,
    get_chat_messages_by_session,
    update_chat_message,
    delete_chat_message,
)
from app.chat_session.chat_session_crud import get_chat_session
from app.chat_message.chat_message_schema import (
    ChatMessageCreate,
    ChatMessageUpdate,
    ChatMessageInDB,
)
from app.db.session import get_db
from app.user.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatMessageInDB)
def create_chat_message_route(
    chat_message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} creating a new chat message")
    chat_session = get_chat_session(db, chat_message.session_id)
    if chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized message creation attempt in session {chat_message.session_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create message in this chat session",
        )
    return create_chat_message(db, chat_message)


@router.get("/{chat_message_id}", response_model=ChatMessageInDB)
def read_chat_message(
    chat_message_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} requesting chat message {chat_message_id}")
    db_chat_message = get_chat_message(db, chat_message_id)
    if db_chat_message is None:
        raise HTTPException(status_code=404, detail="Chat message not found")
    chat_session = get_chat_session(db, db_chat_message.session_id)
    if chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized access attempt to message {chat_message_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this message"
        )
    return db_chat_message


@router.get("/session/{chat_session_id}", response_model=List[ChatMessageInDB])
def read_chat_session_messages(
    chat_session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(
        f"User {current_user.id} requesting messages for chat session {chat_session_id}"
    )
    chat_session = get_chat_session(db, chat_session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized access attempt to messages in session {chat_session_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access messages from this session",
        )
    chat_messages = get_chat_messages_by_session(
        db, chat_session_id, skip=skip, limit=limit
    )
    return chat_messages


@router.put("/{chat_message_id}", response_model=ChatMessageInDB)
def update_chat_message_route(
    chat_message_id: str,
    chat_message: ChatMessageUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} updating chat message {chat_message_id}")
    db_chat_message = get_chat_message(db, chat_message_id)
    if db_chat_message is None:
        raise HTTPException(status_code=404, detail="Chat message not found")
    chat_session = get_chat_session(db, db_chat_message.session_id)
    if chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized update attempt to message {chat_message_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to update this message"
        )
    return update_chat_message(db, chat_message_id, chat_message)


@router.delete("/{chat_message_id}", response_model=ChatMessageInDB)
def delete_chat_message_route(
    chat_message_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} deleting chat message {chat_message_id}")
    db_chat_message = get_chat_message(db, chat_message_id)
    if db_chat_message is None:
        raise HTTPException(status_code=404, detail="Chat message not found")
    chat_session = get_chat_session(db, db_chat_message.session_id)
    if chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized delete attempt to message {chat_message_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this message"
        )
    return delete_chat_message(db, chat_message_id)
