from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_db
from src.core.security import get_current_user_id
from src.exceptions import InvalidBotTokenError
from src.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SuccessResponse,
    TelegramAuth,
    TelegramBotAuth,
    Token,
)
from src.service.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


def verify_telegram_bot_internal_token(
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
) -> None:
    if (
        not settings.TELEGRAM_BOT_INTERNAL_TOKEN
        or x_telegram_bot_token != settings.TELEGRAM_BOT_INTERNAL_TOKEN
    ):
        raise InvalidBotTokenError()


@auth_router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, payload)


@auth_router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh(db, payload)


@auth_router.post("/logout", response_model=SuccessResponse)
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.logout(db, payload.refresh_token)
    return {"success": True}


@auth_router.post("/logout-all", response_model=SuccessResponse)
async def logout_all(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.logout_all(db, user_id)
    return {"success": True}

@auth_router.post("/telegram", response_model=Token)
async def telegram_auth(payload: TelegramAuth, db: AsyncSession = Depends(get_db)):
    return await auth_service.telegram_auth(db, payload)


@auth_router.post("/telegram/bot", response_model=Token)
async def telegram_bot_auth(
    payload: TelegramBotAuth,
    _: None = Depends(verify_telegram_bot_internal_token),
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.telegram_bot_auth(db, payload)
