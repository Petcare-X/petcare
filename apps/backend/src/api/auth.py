from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.schemas.auth import LoginRequest, RefreshRequest, TelegramAuth, Token
from src.service.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()

@auth_router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, payload)

@auth_router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh(db, payload)

@auth_router.post("/telegram", response_model=Token)
async def telegram_auth(payload: TelegramAuth, db: AsyncSession = Depends(get_db)):
    return await auth_service.telegram_auth(db, payload)