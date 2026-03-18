from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.service import SharingService

from src.schemas import InviteCreate, InviteResponse, AcceptInvite

sharing_router = APIRouter(prefix="/invites", tags=["invites"], )

sharing_service = SharingService()

@sharing_router.post("/", status_code=201)
async def create_invite(user_id: int,
                        payload: InviteCreate,
                        db: AsyncSession = Depends(get_db)):
    try:
        invite = await sharing_service.create_invite(user_id, db, payload)
        if invite:
            return {
                "message": "Invite created succesfully", 
                "invite": invite
                }
    except ValueError as e:
        raise HTTPException(status_code=409, 
                            detail=str(e))

@sharing_router.get("/", status_code=200)
async def get_invite(invite_code: str, 
                    db: AsyncSession = Depends(get_db)):
    try:
        invite = await sharing_service.get_invite(db, invite_code)
        if invite:
            return {
                "message": "Invite found", 
                "invite": invite
            }
    except ValueError as e:
        raise HTTPException(status_code=404, 
                            detail=str(e))

@sharing_router.get("/{pet_id}", status_code=200)
async def get_shared_users(pet_id: int, 
                            db: AsyncSession = Depends(get_db)):
    try:
        shared_users = await sharing_service.get_shared_users(db, pet_id)
        if shared_users:
            return {
                "message": "Shared users found", 
                "users": shared_users
            }
    except ValueError as e:
        raise HTTPException(status_code=404, 
                            detail=str(e))

@sharing_router.delete("/{user_id}", status_code=200)
async def delete_invite(user_id: int,
                        invite_code: str,
                        db: AsyncSession = Depends(get_db)):
    ok = await sharing_service.deactivate_invite(db, user_id, invite_code)
    if not ok:
        raise HTTPException(status_code=404,
                            detail="Invite not found")
    return ok

@sharing_router.post("/accept", status_code=202)
async def accept_invite(user_id: int,
                        invite_code: str,
                        db: AsyncSession = Depends(get_db)):
    try:
        await sharing_service.accept_invite(db, user_id, invite_code)
        return {
            "message": "Invite accepted succesfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=403,
                            detail=str(e))