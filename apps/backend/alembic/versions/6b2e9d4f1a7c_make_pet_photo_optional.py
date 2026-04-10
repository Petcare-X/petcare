"""make pet photo optional

Revision ID: 6b2e9d4f1a7c
Revises: f4b2c8d1e6a3
Create Date: 2026-04-08 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6b2e9d4f1a7c"
down_revision: Union[str, Sequence[str], None] = "f4b2c8d1e6a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "pets_info",
        "pet_photo_object_key",
        existing_type=sa.Text(),
        nullable=True,
    )
    op.execute(
        """
        UPDATE pets_info
        SET pet_photo_object_key = NULL
        WHERE pet_photo_object_key = '';
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE pets_info
        SET pet_photo_object_key = ''
        WHERE pet_photo_object_key IS NULL;
        """
    )
    op.alter_column(
        "pets_info",
        "pet_photo_object_key",
        existing_type=sa.Text(),
        nullable=False,
    )
