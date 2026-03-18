from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime, timezone

from src.core import settings

class InviteCreate(BaseModel):
    pet_id: int
    max_uses: Optional[int] = Field(None, gt=0)
    expires_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("expires_at")
    def validate_expires_at(cls, v):
        if v:
            now_utc = datetime.now(timezone.utc)
            if v < now_utc:
                raise ValueError('date and time cannot be in past')
        return v


class InviteResponse(BaseModel):
    invite_url: str = settings.INVITE_BASE_URL
    invite_code: str

    model_config = ConfigDict(from_attributes=True)

class AcceptInvite(BaseModel):
    invite_code: str
    model_config = ConfigDict(from_attributes=True)

class SharedUserResponse(BaseModel):
    pet_id: int
    pet_name: str
    shared_with_user_id: int
    shared_with_user_name: str
    shared_till: datetime
    
    model_config = ConfigDict(from_attributes=True)