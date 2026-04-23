from datetime import datetime, timezone
from src.models import SharedUser
from sqlalchemy import or_

def active_shared_access_clause(
    shared_user_id: int | None = None,
    pet_id: int | None = None,
):
    conditions = [
        or_(
            SharedUser.sharing_end.is_(None),
            SharedUser.sharing_end > datetime.now(timezone.utc),
        ),
    ]
    if shared_user_id is not None:
        conditions.append(SharedUser.shared_user_id == shared_user_id)
    if pet_id is not None:
        conditions.append(SharedUser.shared_pet_id == pet_id)
    return conditions