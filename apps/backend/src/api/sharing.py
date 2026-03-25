from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.security import get_current_user_id
from src.service import SharingService

from src.schemas import AcceptInvite, InviteCreate, InviteResponse, SharedUserResponse

sharing_router = APIRouter(prefix="/invites", tags=["invites"], )

sharing_service = SharingService()

@sharing_router.post("/", status_code=201, response_model=InviteResponse)
async def create_invite(
    payload: InviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.create_invite(current_user_id, db, payload)

@sharing_router.get("/", status_code=200, response_model=InviteResponse)
async def get_invite(invite_code: str, 
                    db: AsyncSession = Depends(get_db)):
    return await sharing_service.get_invite(db, invite_code)

@sharing_router.get("/{pet_id}", status_code=200, response_model=list[SharedUserResponse])
async def get_shared_users(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.get_shared_users(db, pet_id, current_user_id)

@sharing_router.delete("/", status_code=200)
async def delete_invite(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.deactivate_invite(db, invite_code, current_user_id)

@sharing_router.post("/accept", status_code=202)
async def accept_invite(
    payload: AcceptInvite,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await sharing_service.accept_invite(db, payload.invite_code, current_user_id)
    return {
        "message": "Invite accepted succesfully"
    }
