from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from redis.asyncio import Redis
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.configs import settings
from app.user.user_crud import get_user_by_social_id
from app.db.session import get_db
from app.user.token_schema import TokenPayload
from app.user.user_model import User
from app.configs.redis import get_redis
from app.user.security import (
    create_access_token,
    create_refresh_token,
    save_tokens_to_redis,
)
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if (token_data.exp - datetime.now(timezone.utc)) < timedelta(
            settings.ACCESS_TOKEN_PREEMPTIVE_REFRESH_MINUTES
        ):
            refresh_token = await redis.get(f"refresh_token:{token_data.sub}")
            if refresh_token:
                new_access_token = create_access_token(
                    token_data.sub, token_data.provider
                )
                new_refresh_token = create_refresh_token(
                    token_data.sub, token_data.provider
                )
                user = await get_user_by_social_id(
                    db, social_id=token_data.sub, provider=token_data.provider
                )
                if user:
                    await save_tokens_to_redis(
                        redis, user.id, new_access_token, new_refresh_token
                    )

                    token = new_access_token
                    payload = jwt.decode(
                        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                    )
                    token_data = TokenPayload(**payload)
        if token_data.exp < datetime.now(timezone.utc):
            raise credentials_exception
        if token_data.type != "access":
            raise credentials_exception
    except (jwt.JWTError, ValidationError):
        raise credentials_exception

    user = await get_user_by_social_id(
        db, social_id=token_data.sub, provider=token_data.provider
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
