from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.security import get_current_user_id
from src.schemas.auth import SuccessResponse
from src.schemas import AcceptInvite, InviteCreate, InviteResponse, SharedUserResponse
from src.service import SharingService

invites_router = APIRouter(prefix="/invites", tags=["invites"])
pet_shares_router = APIRouter(tags=["pet-sharing"])

sharing_service = SharingService()


@invites_router.post("", status_code=201, response_model=InviteResponse)
async def create_invite(
    payload: InviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.create_invite(current_user_id, db, payload)


@invites_router.get("", status_code=200, response_model=InviteResponse)
async def get_invite(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await sharing_service.get_invite(db, invite_code)


@pet_shares_router.get("/shared-users", status_code=200, response_model=list[SharedUserResponse])
async def get_shared_users(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.get_shared_users(db, pet_id, current_user_id)


@pet_shares_router.delete("/access/{user_id}", status_code=200, response_model=SuccessResponse)
async def remove_access(
    pet_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await sharing_service.revoke_access(db, current_user_id, pet_id, user_id)
    return {"success": True}


@invites_router.delete("", status_code=200, response_model=SuccessResponse)
async def delete_invite(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await sharing_service.deactivate_invite(db, invite_code, current_user_id)
    return {"success": True}


@invites_router.post("/accept", status_code=202)
async def accept_invite(
    payload: AcceptInvite,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await sharing_service.accept_invite(db, payload.invite_code, current_user_id)
    return {"message": "Invite accepted succesfully"}


@invites_router.get(
    "/{pet_id}",
    status_code=200,
    response_model=list[SharedUserResponse],
    include_in_schema=False,
    deprecated=True,
)
async def get_shared_users_legacy(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.get_shared_users(db, pet_id, current_user_id)
