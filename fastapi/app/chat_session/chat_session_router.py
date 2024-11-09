from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.chat_session.chat_session_crud import (
    create_chat_session,
    get_chat_session,
    update_chat_session,
    delete_chat_session,
    get_chat_sessions,
)
from app.chat_session.chat_session_schema import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionInDB,
)
from app.db.session import get_db
from app.user.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatSessionInDB)
def create_chat_session_route(
    chat_session: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} creating a new chat session")
    chat_session.user_id = current_user.id
    return create_chat_session(db, chat_session)


@router.get("/{chat_session_id}", response_model=ChatSessionInDB)
def read_chat_session(
    chat_session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} requesting chat session {chat_session_id}")
    db_chat_session = get_chat_session(db, chat_session_id)
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if db_chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized access attempt to chat session {chat_session_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this chat session"
        )
    return db_chat_session


@router.get("/", response_model=List[ChatSessionInDB])
def read_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} requesting their chat sessions")
    chat_sessions = get_chat_sessions(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return chat_sessions


@router.put("/{chat_session_id}", response_model=ChatSessionInDB)
def update_chat_session_route(
    chat_session_id: str,
    chat_session: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} updating chat session {chat_session_id}")
    db_chat_session = get_chat_session(db, chat_session_id)
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if db_chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized update attempt to chat session {chat_session_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to update this chat session"
        )
    return update_chat_session(db, chat_session_id, chat_session)


@router.delete("/{chat_session_id}", response_model=ChatSessionInDB)
def delete_chat_session_route(
    chat_session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} deleting chat session {chat_session_id}")
    db_chat_session = get_chat_session(db, chat_session_id)
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if db_chat_session.user_id != current_user.id:
        logger.warning(
            f"Unauthorized delete attempt to chat session {chat_session_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this chat session"
        )
    return delete_chat_session(db, chat_session_id)
