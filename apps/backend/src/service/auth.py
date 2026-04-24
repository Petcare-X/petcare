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
    InvalidCredentialsError,
    InvalidTokenError,
    RefreshTokenError,
    RefreshTokenNotFoundError,
)
from src.models import RefreshToken, UserInfo, AuthIdentities
from src.repositories import UsersRepository
from src.schemas.auth import LoginRequest, TelegramAuth, TelegramBotAuth, Token

class AuthService:
    def __init__(self):
        self.repo = UsersRepository()

    async def get_or_create_user_by_telegram(
        self,
        db: AsyncSession,
        telegram_id: int,
        first_name: str,
        photo_url: str | None = None,
    ) -> tuple[UserInfo, bool]:
        auth_identity = await self.repo.get_auth_by_tg(db, telegram_id)

        if auth_identity:
            user_id = auth_identity.user_id
            user = await self.repo.get_by_id(db, user_id)
            return user, False

        user = UserInfo(
            user_name=first_name,
            user_photo=photo_url,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        auth_identity = AuthIdentities(
            user_id=user.id,
            user_telegram_id=telegram_id,
            provider = "telegram"
        )
        db.add(auth_identity)
        await db.commit()
        await db.refresh(auth_identity)

        return user, True

    async def login(self, db: AsyncSession, payload: LoginRequest) -> Token:
        auth_identity = await self.repo.get_auth_by_email(db, str(payload.email))

        if not auth_identity:
            raise InvalidCredentialsError()

        if not verify_password(payload.password, auth_identity.user_password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(auth_identity.user_id)
        refresh_token = await create_refresh_token(auth_identity.user_id, db)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def refresh(self, db: AsyncSession, refresh_token: str) -> Token:
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

        user, _ = await self.get_or_create_user_by_telegram(
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
        user, _ = await self.get_or_create_user_by_telegram(
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
