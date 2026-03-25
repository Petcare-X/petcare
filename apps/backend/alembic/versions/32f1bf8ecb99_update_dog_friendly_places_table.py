"""reshape dog-friendly places table

Revision ID: 32f1bf8ecb99
Revises: f9cd5961f532
Create Date: 2026-03-23 23:55:37.053026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32f1bf8ecb99'
down_revision: Union[str, Sequence[str], None] = 'f9cd5961f532'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_city', sa.String(length=50), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_street', sa.String(length=127), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_building_number', sa.String(length=20), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_lat', sa.Numeric(), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_lon', sa.Numeric(), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_geocoder_precision', sa.String(length=50), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_working_hours', sa.String(length=255), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_is_24_7', sa.Boolean(), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_status', sa.String(length=20), nullable=True))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_last_verified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

    op.execute(
        """
        UPDATE dog_friendly_places
        SET
            dogfriendly_place_city = COALESCE(dogfriendly_place_city, ''),
            dogfriendly_place_street = COALESCE(dogfriendly_place_street, dogfriendly_place_address, ''),
            dogfriendly_place_building_number = COALESCE(dogfriendly_place_building_number, ''),
            dogfriendly_place_geocoder_precision = COALESCE(dogfriendly_place_geocoder_precision, 'unknown'),
            dogfriendly_place_working_hours = COALESCE(dogfriendly_place_working_hours, dogfriendly_place_work_hours),
            dogfriendly_place_status = COALESCE(dogfriendly_place_status, 'active'),
            dogfriendly_place_is_24_7 = COALESCE(dogfriendly_place_is_24_7, FALSE)
        """
    )

    op.alter_column('dog_friendly_places', 'dogfriendly_place_city', existing_type=sa.String(length=50), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_street', existing_type=sa.String(length=127), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_building_number', existing_type=sa.String(length=20), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_lat', existing_type=sa.Numeric(), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_lon', existing_type=sa.Numeric(), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_geocoder_precision', existing_type=sa.String(length=50), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_working_hours', existing_type=sa.String(length=255), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_is_24_7', existing_type=sa.Boolean(), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_status', existing_type=sa.String(length=20), nullable=False)
    op.alter_column('dog_friendly_places', 'dogfriendly_place_last_verified', existing_type=sa.DateTime(timezone=True), nullable=False)

    op.execute("ALTER TABLE dog_friendly_places DROP COLUMN IF EXISTS dogfriendly_place_rating")
    op.execute("ALTER TABLE dog_friendly_places DROP COLUMN IF EXISTS dogfriendly_place_address")
    op.execute("ALTER TABLE dog_friendly_places DROP COLUMN IF EXISTS dogfriendly_place_photo")
    op.execute("ALTER TABLE dog_friendly_places DROP COLUMN IF EXISTS dogfriendly_place_work_hours")
    op.execute("ALTER TABLE dog_friendly_places DROP COLUMN IF EXISTS dogfriendly_place_description")
    op.execute("ALTER TABLE dog_friendly_places DROP COLUMN IF EXISTS dogfriendly_place_contacts")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_contacts', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_description', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_work_hours', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_photo', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_address', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('dog_friendly_places', sa.Column('dogfriendly_place_rating', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.drop_column('dog_friendly_places', 'dogfriendly_place_last_verified')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_status')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_is_24_7')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_working_hours')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_geocoder_precision')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_lon')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_lat')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_building_number')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_street')
    op.drop_column('dog_friendly_places', 'dogfriendly_place_city')
