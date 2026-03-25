"""add unique constraints for dog-friendly places and vet clinics

Revision ID: 4773b39cfdbb
Revises: 32f1bf8ecb99
Create Date: 2026-03-24 00:03:23.537403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4773b39cfdbb'
down_revision: Union[str, Sequence[str], None] = '32f1bf8ecb99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'unique_dog_friendly_place'
            ) THEN
                ALTER TABLE dog_friendly_places
                ADD CONSTRAINT unique_dog_friendly_place
                UNIQUE (dogfriendly_place_name, dogfriendly_place_city, dogfriendly_place_street, dogfriendly_place_building_number);
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'unique_vet_clinic'
            ) THEN
                ALTER TABLE vet_clinics
                ADD CONSTRAINT unique_vet_clinic
                UNIQUE (vet_name, vet_city, vet_street, vet_building_number);
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE vet_clinics DROP CONSTRAINT IF EXISTS unique_vet_clinic")
    op.execute("ALTER TABLE dog_friendly_places DROP CONSTRAINT IF EXISTS unique_dog_friendly_place")
