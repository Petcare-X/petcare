from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    create_access_token,
    create_refresh_token,
    delete_expired_refresh_tokens,
    decode_token,
    verify_telegram_auth,
    verify_password,
)
from src.exceptions import (
    AuthProviderMismatchError,
    InvalidCredentialsError,
    InvalidTokenError,
    RefreshTokenError,
    RefreshTokenNotFoundError,
)
from src.models import RefreshToken, UserInfo
from src.schemas.auth import LoginRequest, RefreshRequest, TelegramAuth, TelegramBotAuth, Token

class AuthService:
    async def get_or_create_telegram_user(
        self,
        db: AsyncSession,
        telegram_id: int,
        first_name: str,
        photo_url: str | None = None,
    ) -> tuple[UserInfo, bool]:
        result = await db.execute(
            select(UserInfo).where(UserInfo.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            return user, False

        user = UserInfo(
            user_name=first_name,
            user_email=f"tg_{telegram_id}@telegram.local",
            user_password_hash="telegram_auth_only",
            user_phone_number=f"+100000{telegram_id}"[:16],
            user_date_of_birth=datetime(1970, 1, 1).date(),
            user_photo=photo_url,
            telegram_id=telegram_id,
            auth_provider="telegram",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user, True

    async def login(self, db: AsyncSession, payload: LoginRequest) -> Token:
        result = await db.execute(
            select(UserInfo).where(UserInfo.user_email == str(payload.email))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError()

        if user.auth_provider != "email":
            raise AuthProviderMismatchError()

        if not verify_password(payload.password, user.user_password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(user.id)
        refresh_token = await create_refresh_token(user.id, db)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    
    async def refresh(self, db: AsyncSession, payload: RefreshRequest) -> Token:
        await delete_expired_refresh_tokens(db)

        token_payload = decode_token(payload.refresh_token)
        if not token_payload:
            raise RefreshTokenError()

        if token_payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")

        sub = token_payload.get("sub")
        jti = token_payload.get("jti")
        if not sub or not jti:
            raise RefreshTokenError()

        token_row = await db.execute(
            select(RefreshToken).where(RefreshToken.token_jti == jti)
        )
        stored_token = token_row.scalar_one_or_none()

        if not stored_token:
            raise RefreshTokenNotFoundError()

        if stored_token.user_id != int(sub):
            raise InvalidTokenError("Refresh token subject mismatch")

        if stored_token.revoked:
            raise InvalidTokenError("Refresh token revoked")

        if stored_token.expires_at <= datetime.now(timezone.utc):
            raise InvalidTokenError("Refresh token expired")

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
            raise InvalidCredentialsError("Invalid Telegram auth data")

        user, _ = await self.get_or_create_telegram_user(
            db,
            payload.id,
            payload.first_name,
            str(payload.photo_url) if payload.photo_url else None,
        )

        access_token = create_access_token(user.id)
        refresh_token = await create_refresh_token(user.id, db)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def telegram_bot_auth(self, db: AsyncSession, payload: TelegramBotAuth) -> Token:
        user, _ = await self.get_or_create_telegram_user(
            db,
            payload.id,
            payload.first_name,
            str(payload.photo_url) if payload.photo_url else None,
        )

        access_token = create_access_token(user.id)
        refresh_token = await create_refresh_token(user.id, db)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, db: AsyncSession, refresh_token: str) -> None:
        await delete_expired_refresh_tokens(db)

        token_payload = decode_token(refresh_token)
        if not token_payload:
            raise RefreshTokenError()

        if token_payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")

        sub = token_payload.get("sub")
        jti = token_payload.get("jti")
        if not sub or not jti:
            raise RefreshTokenError()

        user_id = int(sub)

        token_row = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.token_jti == jti,
            )
        )
        stored_token = token_row.scalar_one_or_none()

        if not stored_token:
            raise RefreshTokenNotFoundError()

        if stored_token.revoked:
            return

        stored_token.revoked = True
        await db.commit()
        
    async def logout_all(self, db: AsyncSession, user_id: int) -> None:
        await delete_expired_refresh_tokens(db)

        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await db.commit()
