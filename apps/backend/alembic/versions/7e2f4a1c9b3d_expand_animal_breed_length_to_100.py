"""expand animal breed length to 100

Revision ID: 7e2f4a1c9b3d
Revises: da3d817a5e07
Create Date: 2026-05-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e2f4a1c9b3d'
down_revision: Union[str, Sequence[str], None] = 'da3d817a5e07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'animals_breeds',
        'animal_breed',
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'animals_breeds',
        'animal_breed',
        existing_type=sa.String(length=100),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
