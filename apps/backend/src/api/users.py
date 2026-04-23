from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.service import UsersService

from src.core.security import get_current_user
from src.models import UserInfo

from src.schemas.users import CreateUser, UpdateUser, UserPrivate, LinkEmail, LinkTelegram

users_router = APIRouter(prefix="/users", tags=["users"])

users_service = UsersService()

@users_router.post("", response_model=UserPrivate, status_code=201)
async def create(payload: CreateUser, db: AsyncSession = Depends(get_db)):
    user = await users_service.create_user(db, payload)
    return users_service.to_private_response(user)

@users_router.get("/me", response_model=UserPrivate)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    return users_service.to_private_response(current_user)

@users_router.patch("/me/data", response_model=UserPrivate)
async def patch_data(
    payload: UpdateUser,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.update_user(current_user.id, payload, db)
    return users_service.to_private_response(user)

@users_router.patch("/me/contacts", response_model=UserPrivate)
async def patch_contacts(
    payload: UpdateUser,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.update_user(current_user.id, payload, db)
    return users_service.to_private_response(user)

@users_router.delete("/me")
async def remove(
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await users_service.delete_user(db, current_user.id)
    return {"deleted": True}

@users_router.get("/{user_id}", include_in_schema=False, response_model=UserPrivate)
async def get(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        from src.exceptions import UserNotFoundError
        raise UserNotFoundError()
    return users_service.to_private_response(user)

@users_router.get("", include_in_schema=False, response_model=list[UserPrivate])
async def list_users(db: AsyncSession = Depends(get_db), offset: int = 0, limit: int = 50):
    users = await users_service.list_all_users(db=db, offset=offset, limit=limit)
    return [users_service.to_private_response(user) for user in users]

@users_router.get("/link-email/{user_id}")
async def link_email_login(
    payload: LinkEmail,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ok = await users_service.link_email_login(db, current_user.id, payload.user_email)
    return {"linked": ok}

@users_router.get("/link-telegram/{user_id}")
async def link_telegram_login(
    payload: LinkTelegram,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ok = await users_service.link_telegram_login(db, current_user.id, payload.telegram_id)
    return {"linked": ok}