from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
from app.user.auth import get_current_active_user, get_current_user
import logging
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatSessionInDB)
def create_chat_session_route(
    session_id: str = 1,  # room_id가 세션 ID로 사용됨
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    logger.info(
        f"User {current_user.id} creating a new chat session for room {session_id}"
    )

    # Check if session for the room already exists
    existing_session = get_chat_session(db, session_id)
    if existing_session:
        return existing_session

    # Create new session if it doesn't exist
    chat_session = ChatSessionCreate(id=session_id, user_id=current_user.id)
    return create_chat_session(db, chat_session)
