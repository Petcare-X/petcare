"""reshape vet clinics table

Revision ID: ec43268b0a8e
Revises: 7c3d9a2f1b6e
Create Date: 2026-03-23 23:28:14.038159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec43268b0a8e'
down_revision: Union[str, Sequence[str], None] = '7c3d9a2f1b6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = 'b2bc761f460a'


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pet_id_created_by
        ON pet_invite (pet_id, created_by)
        """
    )

    op.add_column('vet_clinics', sa.Column('vet_name', sa.String(length=50), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_city', sa.String(length=50), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_street', sa.String(length=127), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_building_number', sa.String(length=6), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_lat', sa.Numeric(), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_lon', sa.Numeric(), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_geocoder_precision', sa.String(length=50), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_working_hours', sa.String(length=255), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_is_24_7', sa.Boolean(), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_status', sa.String(length=20), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_phone', sa.String(length=16), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_website', sa.Text(), nullable=True))
    op.add_column('vet_clinics', sa.Column('vet_last_verified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

    op.execute(
        """
        UPDATE vet_clinics
        SET
            vet_name = COALESCE(vet_name, vet_clinic_name),
            vet_working_hours = COALESCE(vet_working_hours, vet_clinic_work_hours),
            vet_phone = COALESCE(vet_phone, vet_clinic_contacts),
            vet_city = COALESCE(vet_city, ''),
            vet_street = COALESCE(vet_street, vet_clinic_address, ''),
            vet_building_number = COALESCE(vet_building_number, ''),
            vet_geocoder_precision = COALESCE(vet_geocoder_precision, 'unknown'),
            vet_status = COALESCE(vet_status, 'active'),
            vet_is_24_7 = COALESCE(vet_is_24_7, FALSE)
        """
    )

    op.alter_column('vet_clinics', 'vet_name', existing_type=sa.String(length=50), nullable=False)
    op.alter_column('vet_clinics', 'vet_city', existing_type=sa.String(length=50), nullable=False)
    op.alter_column('vet_clinics', 'vet_street', existing_type=sa.String(length=127), nullable=False)
    op.alter_column('vet_clinics', 'vet_building_number', existing_type=sa.String(length=6), nullable=False)
    op.alter_column('vet_clinics', 'vet_lat', existing_type=sa.Numeric(), nullable=False)
    op.alter_column('vet_clinics', 'vet_lon', existing_type=sa.Numeric(), nullable=False)
    op.alter_column('vet_clinics', 'vet_geocoder_precision', existing_type=sa.String(length=50), nullable=False)
    op.alter_column('vet_clinics', 'vet_working_hours', existing_type=sa.String(length=255), nullable=False)
    op.alter_column('vet_clinics', 'vet_is_24_7', existing_type=sa.Boolean(), nullable=False)
    op.alter_column('vet_clinics', 'vet_status', existing_type=sa.String(length=20), nullable=False)
    op.alter_column('vet_clinics', 'vet_last_verified', existing_type=sa.DateTime(timezone=True), nullable=False)

    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_work_hours")
    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_rating")
    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_description")
    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_name")
    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_photo")
    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_address")
    op.execute("ALTER TABLE vet_clinics DROP COLUMN IF EXISTS vet_clinic_contacts")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('vet_clinics', sa.Column('vet_clinic_contacts', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('vet_clinics', sa.Column('vet_clinic_address', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('vet_clinics', sa.Column('vet_clinic_photo', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('vet_clinics', sa.Column('vet_clinic_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('vet_clinics', sa.Column('vet_clinic_description', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('vet_clinics', sa.Column('vet_clinic_rating', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.add_column('vet_clinics', sa.Column('vet_clinic_work_hours', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.drop_column('vet_clinics', 'vet_last_verified')
    op.drop_column('vet_clinics', 'vet_website')
    op.drop_column('vet_clinics', 'vet_phone')
    op.drop_column('vet_clinics', 'vet_status')
    op.drop_column('vet_clinics', 'vet_is_24_7')
    op.drop_column('vet_clinics', 'vet_working_hours')
    op.drop_column('vet_clinics', 'vet_geocoder_precision')
    op.drop_column('vet_clinics', 'vet_lon')
    op.drop_column('vet_clinics', 'vet_lat')
    op.drop_column('vet_clinics', 'vet_building_number')
    op.drop_column('vet_clinics', 'vet_street')
    op.drop_column('vet_clinics', 'vet_city')
    op.drop_column('vet_clinics', 'vet_name')
    op.execute("DROP INDEX IF EXISTS ix_pet_id_created_by")
