import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.RefreshToken import RefreshToken

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"pbkdf2_sha256${salt}${dk.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt, hexhash = stored.split("$", 2)
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
        return secrets.compare_digest(dk.hex(), hexhash)
    except Exception:
        return False
    
def verify_telegram_auth(data: dict) -> bool:
    received_hash = data.get("hash")
    if not received_hash:
        return False

    auth_date = data.get("auth_date")
    if auth_date is None:
        return False

    try:
        auth_timestamp = int(auth_date)
    except (TypeError, ValueError):
        return False

    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    if now_timestamp - auth_timestamp > 24 * 60 * 60:
        return False

    if not settings.TELEGRAM_BOT_TOKEN:
        return False

    check_data = {
        key: value
        for key, value in data.items()
        if key != "hash" and value is not None
    }

    data_check_string = "\n".join(
        f"{key}={check_data[key]}"
        for key in sorted(check_data.keys())
    )

    secret_key = hashlib.sha256(
        settings.TELEGRAM_BOT_TOKEN.encode("utf-8")
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(calculated_hash, received_hash)
    
def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def create_refresh_token(user_id: int, db: AsyncSession) -> str:
    now = datetime.now(timezone.utc)
    jti = str(uuid4())
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "refresh",
        "jti": jti,
    }

    refresh_token = RefreshToken(
        user_id=user_id,
        token_jti=jti,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(refresh_token)
    await db.commit()

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except Exception:
        return None

def verify_access_token(token: str) -> int | None:
    payload = decode_token(token)
    if not payload:
        return None

    if payload.get("type") != "access":
        return None

    sub = payload.get("sub")
    if sub is None:
        return None

    try:
        return int(sub)
    except (TypeError, ValueError):
        return None