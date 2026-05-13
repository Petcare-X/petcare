from fastapi import APIRouter, Depends, Header, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_db
from src.core.security import get_current_user_id
from src.exceptions import InvalidBotTokenError, RefreshTokenError
from src.schemas.auth import (
    AccessToken,
    LoginRequest,
    SuccessResponse,
    TelegramAuth,
    TelegramBotAuth,
    Token,
)
from src.service.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENV != "dev",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/auth",
    )


def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/auth",
        httponly=True,
        secure=settings.ENV != "dev",
        samesite="lax",
    )


def verify_telegram_bot_internal_token(
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
) -> None:
    if (
        not settings.TELEGRAM_BOT_INTERNAL_TOKEN
        or x_telegram_bot_token != settings.TELEGRAM_BOT_INTERNAL_TOKEN
    ):
        raise InvalidBotTokenError()


@auth_router.post("/login", response_model=AccessToken)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    tokens = await auth_service.login(db, payload)
    set_refresh_cookie(response, tokens.refresh_token)
    return AccessToken(access_token=tokens.access_token)


@auth_router.post("/refresh", response_model=AccessToken)
async def refresh(response: Response, refresh_token: str | None = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        delete_refresh_cookie(response)
        raise RefreshTokenError("Missing refresh token cookie")

    tokens = await auth_service.refresh(db, refresh_token)
    set_refresh_cookie(response, tokens.refresh_token)
    return AccessToken(access_token=tokens.access_token)


@auth_router.post("/logout", response_model=SuccessResponse)
async def logout(response: Response, refresh_token: str | None = Cookie(default=None), db: AsyncSession = Depends(get_db)):
    if refresh_token:
        await auth_service.logout(db, refresh_token)
    delete_refresh_cookie(response)
    return {"success": True}


@auth_router.post("/logout-all", response_model=SuccessResponse)
async def logout_all(
    response: Response,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.logout_all(db, user_id)
    delete_refresh_cookie(response)
    return {"success": True}

@auth_router.post("/telegram", response_model=AccessToken)
async def telegram_auth(payload: TelegramAuth, response: Response, db: AsyncSession = Depends(get_db)):
    tokens = await auth_service.telegram_auth(db, payload)
    set_refresh_cookie(response, tokens.refresh_token)
    return AccessToken(access_token=tokens.access_token)


@auth_router.post("/telegram/bot", response_model=Token)
async def telegram_bot_auth(
    payload: TelegramBotAuth,
    _: None = Depends(verify_telegram_bot_internal_token),
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.telegram_bot_auth(db, payload)
