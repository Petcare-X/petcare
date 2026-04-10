"""make user photo optional

Revision ID: 8c4f1b7d2e6a
Revises: 6b2e9d4f1a7c
Create Date: 2026-04-08 12:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8c4f1b7d2e6a"
down_revision: Union[str, Sequence[str], None] = "6b2e9d4f1a7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users_info",
        "user_photo",
        existing_type=sa.Text(),
        nullable=True,
    )
    op.execute(
        """
        UPDATE users_info
        SET user_photo = NULL
        WHERE user_photo = '';
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE users_info
        SET user_photo = ''
        WHERE user_photo IS NULL;
        """
    )
    op.alter_column(
        "users_info",
        "user_photo",
        existing_type=sa.Text(),
        nullable=False,
    )
