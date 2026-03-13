from datetime import datetime, timezone
import hashlib
import hmac

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from src.models import RefreshToken, UserInfo
from src.schemas.auth import LoginRequest, RefreshRequest, TelegramAuth, Token

class AuthService:
    async def login(self, db: AsyncSession, payload: LoginRequest) -> Token:
        result = await db.execute(
            select(UserInfo).where(UserInfo.user_email == str(payload.email))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user.auth_provider != "email":
            raise HTTPException(
                status_code=400,
                detail="This account uses a different sign-in method",
            )

        if not verify_password(payload.password, user.user_password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(user.id)
        refresh_token = await create_refresh_token(user.id, db)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def refresh(self, db: AsyncSession, payload: RefreshRequest) -> Token:
        token_payload = decode_token(payload.refresh_token)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if token_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        sub = token_payload.get("sub")
        jti = token_payload.get("jti")
        if not sub or not jti:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        token_row = await db.execute(
            select(RefreshToken).where(RefreshToken.token_jti == jti)
        )
        stored_token = token_row.scalar_one_or_none()

        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh token not found")

        if stored_token.revoked:
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        if stored_token.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token expired")

        stored_token.revoked = True
        await db.commit()

        user_id = int(sub)
        access_token = create_access_token(user_id)
        refresh_token = await create_refresh_token(user_id, db)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def telegram_auth(self, db: AsyncSession, payload: TelegramAuth) -> Token:
        self._verify_telegram_auth(payload)

        result = await db.execute(
            select(UserInfo).where(UserInfo.telegram_id == payload.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = UserInfo(
                user_name=payload.first_name,
                user_email=f"tg_{payload.id}@telegram.local",
                user_password_hash="telegram_auth_only",
                user_phone=f"+100000{payload.id}"[:16],
                user_date_of_birth=datetime(1970, 1, 1).date(),
                user_photo=str(payload.photo_url) if payload.photo_url else "",
                telegram_id=payload.id,
                auth_provider="telegram",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        access_token = create_access_token(user.id)
        refresh_token = await create_refresh_token(user.id, db)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    def _verify_telegram_auth(self, payload: TelegramAuth) -> None:
        data = {
            "auth_date": str(payload.auth_date),
            "first_name": payload.first_name,
            "id": str(payload.id),
        }

        if payload.last_name:
            data["last_name"] = payload.last_name
        if payload.username:
            data["username"] = payload.username
        if payload.photo_url:
            data["photo_url"] = str(payload.photo_url)

        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(data.items())
        )

        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, payload.hash):
            raise HTTPException(status_code=401, detail="Invalid Telegram auth data")
