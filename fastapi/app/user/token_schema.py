from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TokenPayload(BaseModel):
    exp: datetime
    sub: str
    provider: str
    type: str


class Token(BaseModel):
    access_token: str
    token_type: str
