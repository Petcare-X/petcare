"""add pet photo metadata to pets_info

Revision ID: c3f8e2c71a4b
Revises: 9e11ca1f588d
Create Date: 2026-03-18 13:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3f8e2c71a4b"
down_revision: Union[str, Sequence[str], None] = "9e11ca1f588d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "pets_info",
        sa.Column("pet_photo_content_type", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "pets_info",
        sa.Column("pet_photo_size_bytes", sa.BIGINT(), nullable=True),
    )
    op.add_column(
        "pets_info",
        sa.Column("pet_photo_etag", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "pets_info",
        sa.Column("pet_photo_uploaded_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("pets_info", "pet_photo_uploaded_at")
    op.drop_column("pets_info", "pet_photo_etag")
    op.drop_column("pets_info", "pet_photo_size_bytes")
    op.drop_column("pets_info", "pet_photo_content_type")
