from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.user import user_schema
from app.db.session import get_db
from app.user.auth import get_current_active_user
import logging

from app.user import user_crud

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[user_schema.User])
async def read_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user),
):
    users = await user_crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=user_schema.User)
async def read_user_me(
    current_user: user_schema.User = Depends(get_current_active_user),
):
    return current_user


@router.put("/me", response_model=user_schema.User)
async def update_user_me(
    user: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user),
):
    updated_user = await user_crud.update_user(
        db, user_id=current_user.id, user=user
    )
    return updated_user


@router.get("/{user_id}", response_model=user_schema.User)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user),
):
    db_user = await user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
