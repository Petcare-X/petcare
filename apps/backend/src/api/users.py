from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.service.users import (
    create_user, delete_user, get_user_by_id, list_users,
    update_user_contacts, update_user_data
)
from src.schemas.users import CreateUser, UpdateContactsUser, UpdateDataUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
async def create(payload: CreateUser, db: AsyncSession = Depends(get_db)):
    try:
        user = await create_user(db, payload)
        if user:
            return {"message": "User created succesfully"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/{user_id}")
async def get(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.get("")
async def list_(db: AsyncSession = Depends(get_db), offset: int = 0, limit: int = 50):
    return await list_users(db, offset, limit)


@router.patch("/{user_id}/data")
async def patch_data(user_id: int, payload: UpdateDataUser, db: AsyncSession = Depends(get_db)):
    user = await update_user_data(db, user_id, payload)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch("/{user_id}/contacts")
async def patch_contacts(user_id: int, payload: UpdateContactsUser, db: AsyncSession = Depends(get_db)):
    try:
        user = await update_user_contacts(db, user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.delete("/{user_id}")
async def remove(user_id: int, db: AsyncSession = Depends(get_db)):
    ok = await delete_user(db, user_id)
    if not ok:
        raise HTTPException(404, "User not found")
    return {"deleted": True}