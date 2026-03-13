from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Literal

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TelegramAuth(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: HttpUrl | None = None
    auth_date: int
    hash: str