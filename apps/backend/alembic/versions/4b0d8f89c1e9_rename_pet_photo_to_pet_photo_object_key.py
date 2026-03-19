"""rename pet_photo to pet_photo_object_key

Revision ID: 4b0d8f89c1e9
Revises: c3f8e2c71a4b
Create Date: 2026-03-18 13:40:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4b0d8f89c1e9"
down_revision: Union[str, Sequence[str], None] = "c3f8e2c71a4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("pets_info", "pet_photo", new_column_name="pet_photo_object_key")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("pets_info", "pet_photo_object_key", new_column_name="pet_photo")
