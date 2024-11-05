import aiohttp
from redis.asyncio import Redis
from typing import Optional, Tuple, Dict
from fastapi import HTTPException
from pydantic import ValidationError
from app.configs import settings
from app.user.user_crud import get_user_by_social_id, create_user
from app.user.user_schema import UserCreate
from app.user.token_schema import TokenPayload
from app.user.user_model import User, Gender, SocialProvider
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)


async def fetch_token(url: str, data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400, detail="Invalid authorization code"
                )
            return await response.json()


async def fetch_user_info(url: str, headers: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=400, detail="Invalid access token")
            return await response.json()


async def save_tokens_to_redis(redis: Redis, user_id, access_token, refresh_token):
    access_token_expiry = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_token_expiry = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    await redis.setex(f"access_token:{user_id}", access_token_expiry, access_token)
    await redis.setex(f"refresh_token:{user_id}", refresh_token_expiry, refresh_token)


async def get_tokens_from_redis(redis: Redis, user_id):
    access_token = await redis.get(f"access_token:{user_id}")
    refresh_token = await redis.get(f"refresh_token:{user_id}")
    return access_token, refresh_token


async def delete_tokens_from_redis(redis: Redis, user_id: str):
    await redis.delete(f"access_token:{user_id}", f"refresh_token:{user_id}")


async def logout(user_id: str, redis: Redis):
    await delete_tokens_from_redis(redis, user_id)


async def update_last_login(db: AsyncSession, user: User):
    user.last_login = datetime.now()
    db.add(user)
    await db.commit()
    await db.refresh(user)


def create_access_token(
    social_id: str, provider: str, expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": social_id,
        "provider": provider,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(social_id: str, provider: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {
        "exp": expires,
        "sub": social_id,
        "provider": provider,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.exp < datetime.now(timezone.utc):
            logger.warning(f"{token_type.capitalize()} token has expired")
            return None
        if token_data.type != token_type:
            logger.warning(f"Invalid {token_type} token type")
            return None
        return token_data
    except JWTError as e:
        logger.error(f"JWT decode error in {token_type} token: {str(e)}")
        return None
    except ValidationError as e:
        logger.error(f"{token_type.capitalize()} token validation error: {str(e)}")
        return None


verify_access_token = lambda token: verify_token(token, "access")
verify_refresh_token = lambda token: verify_token(token, "refresh")


async def refresh_access_token(refresh_token: str, db: AsyncSession, redis: Redis):
    token_data = verify_refresh_token(refresh_token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_social_id(db, token_data.sub, token_data.provider)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_refresh_token = await redis.get(f"refresh_token:{user.id}")
    if not stored_refresh_token or stored_refresh_token.decode() != refresh_token:
        raise HTTPException(
            status_code=401, detail="Refresh token is invalid or expired"
        )

    new_access_token = create_access_token(user.social_id, user.social_provider)
    new_refresh_token = create_refresh_token(user.social_id, user.social_provider)
    await save_tokens_to_redis(redis, user.id, new_access_token, new_refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


async def create_tokens_and_login(user: User, redis: Redis):
    access_token = create_access_token(user.social_id, user.social_provider)
    refresh_token = create_refresh_token(user.social_id, user.social_provider)
    await save_tokens_to_redis(redis, user.id, access_token, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def authenticate_user(
    social_id: str, provider: str, user_data: dict, db: AsyncSession, redis: Redis
) -> Tuple[User, Dict]:
    user = await get_user_by_social_id(db, social_id, provider=provider)
    if user:
        await update_last_login(db, user)
    else:
        user_create = UserCreate(
            social_id=social_id, social_provider=provider, **user_data
        )
        user = await create_user(db, user=user_create)
        if user is None:
            logger.error("Failed to create new user")
            raise HTTPException(status_code=400, detail="Failed to create user")

    tokens = await create_tokens_and_login(user, redis)
    return user, tokens


async def authenticate_google(
    code: str, db: AsyncSession, redis: Redis
) -> Tuple[User, Dict]:
    try:
        token_info = await fetch_token(
            "https://oauth2.googleapis.com/token",
            {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        user_info = await fetch_user_info(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            {"Authorization": f"Bearer {token_info['access_token']}"},
        )

        user_data = {
            "email": user_info.get("email"),
            "username": user_info.get("name"),
            "profile_image": user_info.get("picture"),
            "full_name": user_info.get("name"),
            "nickname": user_info.get("given_name"),
            "locale": user_info.get("locale"),
        }

        return await authenticate_user(
            user_info["id"], SocialProvider.GOOGLE, user_data, db, redis
        )
    except Exception as e:
        logger.error(f"Error in authenticate_google: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Failed to authenticate with Google: {str(e)}"
        )


async def authenticate_kakao(
    code: str, db: AsyncSession, redis: Redis
) -> Tuple[User, Dict]:
    try:
        token_info = await fetch_token(
            "https://kauth.kakao.com/oauth/token",
            {
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
            },
        )

        user_info = await fetch_user_info(
            "https://kapi.kakao.com/v2/user/me",
            {"Authorization": f"Bearer {token_info['access_token']}"},
        )

        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        gender = None
        if kakao_account.get("gender") == "male":
            gender = Gender.MALE
        elif kakao_account.get("gender") == "female":
            gender = Gender.FEMALE

        user_data = {
            "email": kakao_account.get("email"),
            "username": profile.get("nickname"),
            "profile_image": profile.get("profile_image_url"),
            "full_name": profile.get("nickname"),
            "nickname": profile.get("nickname"),
            "gender": gender,
            "age_range": kakao_account.get("age_range"),
            "birth_date": (
                parse_kakao_birth_date(kakao_account.get("birthday"))
                if kakao_account.get("birthday")
                else None
            ),
        }

        return await authenticate_user(
            str(user_info["id"]), SocialProvider.KAKAO, user_data, db, redis
        )
    except Exception as e:
        logger.error(f"Error in authenticate_kakao: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Failed to authenticate with Kakao: {str(e)}"
        )


async def authenticate_naver(
    code: str, state: str, db: AsyncSession, redis: Redis
) -> Tuple[User, Dict]:
    try:
        token_info = await fetch_token(
            "https://nid.naver.com/oauth2.0/token",
            {
                "grant_type": "authorization_code",
                "client_id": settings.NAVER_CLIENT_ID,
                "client_secret": settings.NAVER_CLIENT_SECRET,
                "code": code,
                "state": state,
            },
        )
        if token_info is None:
            raise HTTPException(
                status_code=400, detail="Failed to fetch token from Naver"
            )

        user_info = await fetch_user_info(
            "https://openapi.naver.com/v1/nid/me",
            {"Authorization": f"Bearer {token_info['access_token']}"},
        )
        if user_info is None or user_info.get("resultcode") != "00":
            raise HTTPException(
                status_code=400, detail="Failed to fetch user info from Naver"
            )

        naver_response = user_info["response"]

        gender = None
        if naver_response.get("gender") == "M":
            gender = Gender.MALE
        elif naver_response.get("gender") == "F":
            gender = Gender.FEMALE

        user_data = {
            "email": naver_response.get("email"),
            "username": naver_response.get("name"),
            "profile_image": naver_response.get("profile_image"),
            "full_name": naver_response.get("name"),
            "nickname": naver_response.get("nickname"),
            "gender": gender,
            "age_range": naver_response.get("age"),
            "birth_date": parse_naver_birth_date(
                naver_response.get("birthyear"), naver_response.get("birthday")
            ),
            "phone_number": naver_response.get("mobile"),
        }

        return await authenticate_user(
            naver_response["id"], SocialProvider.NAVER, user_data, db, redis
        )
    except Exception as e:
        logger.error(f"Error in authenticate_naver: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Failed to authenticate with Naver: {str(e)}"
        )


def parse_kakao_birth_date(birth_date: str) -> Optional[datetime.date]:
    try:
        today = datetime.now()
        birth_date_this_year = datetime.strptime(
            f"{today.year}{birth_date}", "%Y%m%d"
        ).date()
        return birth_date_this_year
    except ValueError:
        return None


def parse_naver_birth_date(birthyear: str, birthday: str) -> Optional[datetime.date]:
    if not birthday or not birthyear:
        return None
    try:
        return datetime.strptime(f"{birthyear}-{birthday}", "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Invalid birth date format: year={birthyear}, date={birthday}")
        return None
