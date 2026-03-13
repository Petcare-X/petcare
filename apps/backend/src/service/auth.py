from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_telegram_auth,
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
        await db.commit()

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

        if stored_token.user_id != int(sub):
            raise HTTPException(status_code=401, detail="Refresh token subject mismatch")

        if stored_token.revoked:
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        if stored_token.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token expired")

        stored_token.revoked = True

        user_id = int(sub)
        access_token = create_access_token(user_id)
        refresh_token = await create_refresh_token(user_id, db)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def telegram_auth(self, db: AsyncSession, payload: TelegramAuth) -> Token:
        if not verify_telegram_auth(payload.model_dump()):
            raise HTTPException(status_code=401, detail="Invalid Telegram auth data")

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
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, db: AsyncSession, user_id: int, refresh_token: str) -> None:
        token_payload = decode_token(refresh_token)
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if token_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        sub = token_payload.get("sub")
        jti = token_payload.get("jti")
        if not sub or not jti:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if int(sub) != user_id:
            raise HTTPException(status_code=403, detail="Token does not belong to user")

        token_row = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.token_jti == jti,
            )
        )
        stored_token = token_row.scalar_one_or_none()

        if not stored_token:
            raise HTTPException(status_code=404, detail="Refresh token not found")

        if stored_token.revoked:
            return

        stored_token.revoked = True
        await db.commit()
        
    async def logout_all(self, db: AsyncSession, user_id: int) -> None:
        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await db.commit()
