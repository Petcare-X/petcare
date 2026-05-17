from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_db
from src.service import UsersService

from src.core.security import get_current_user
from src.models import UserInfo

from src.schemas.users import CreateUser, UpdateUser, UserPrivate, LinkEmail, LinkTelegram

users_router = APIRouter(prefix="/users", tags=["users"])

users_service = UsersService()

def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=settings.ENV != "dev",
        samesite="lax",
    )

@users_router.post("", response_model=UserPrivate, status_code=201)
async def create(payload: CreateUser, db: AsyncSession = Depends(get_db)):
    user = await users_service.create_user(db, payload)
    return await users_service.to_private_response(db, user)

@users_router.get("/me", response_model=UserPrivate)
async def get_me(current_user: UserInfo = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await users_service.to_private_response(db, current_user)

@users_router.patch("/me/data", response_model=UserPrivate)
async def patch_data(
    payload: UpdateUser,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.update_user(current_user.id, payload, db)
    return await users_service.to_private_response(db, user)

@users_router.patch("/me/contacts", response_model=UserPrivate)
async def patch_contacts(
    payload: UpdateUser,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.update_user(current_user.id, payload, db)
    return await users_service.to_private_response(db, user)

@users_router.delete("/me")
async def remove(
    response: Response,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await users_service.delete_user_with_assets(db, current_user.id)
    delete_refresh_cookie(response)
    return {"deleted": True}

@users_router.get("/{user_id}", include_in_schema=False, response_model=UserPrivate)
async def get(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        from src.exceptions import UserNotFoundError
        raise UserNotFoundError()
    return await users_service.to_private_response(db, user)

@users_router.get("", include_in_schema=False, response_model=list[UserPrivate])
async def list_users(db: AsyncSession = Depends(get_db), offset: int = 0, limit: int = 50):
    users = await users_service.list_all_users(db=db, offset=offset, limit=limit)
    return [await users_service.to_private_response(db, user) for user in users]

@users_router.post("/link-email/{user_id}")
async def link_email_login(
    payload: LinkEmail,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ok = await users_service.link_email_login(db, current_user.id, payload.user_email)
    return {"linked": ok}

@users_router.post("/link-telegram/{user_id}")
async def link_telegram_login(
    payload: LinkTelegram,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ok = await users_service.link_telegram_login(db, current_user.id, payload.telegram_id)
    return {"linked": ok}
