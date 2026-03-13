from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.service import UsersService

from src.core.security import get_current_user, get_current_user_optional
from src.models import UserInfo

from src.schemas.users import CreateUser, UpdateUser

users_router = APIRouter(prefix="/users", tags=["users"])

users_service = UsersService()

@users_router.post("")
async def create(payload: CreateUser, db: AsyncSession = Depends(get_db)):
    try:
        user = await users_service.create_user(db, payload)
        if user:
            return {"message": "User created succesfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@users_router.get("/{user_id}")
async def get(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@users_router.get("")
async def list_users(db: AsyncSession = Depends(get_db), offset: int = 0, limit: int = 50):
    return await users_service.list_all_users(db=db, offset=offset, limit=limit)


@users_router.patch("/{user_id}/data")
async def patch_data(user_id: int, payload: UpdateUser, db: AsyncSession = Depends(get_db)):
    try:
        user = await users_service.update_user(user_id, payload, db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not user:
        raise HTTPException(404, "User not found")
    return user

@users_router.delete("/{user_id}")
async def remove(user_id: int, db: AsyncSession = Depends(get_db)):
    ok = await users_service.delete_user(db, user_id)
    if not ok:
        raise HTTPException(404, "User not found")
    return {"deleted": True}