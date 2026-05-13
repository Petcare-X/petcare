"""recover map schema before salons

Revision ID: 5b0f8d4a7c21
Revises: 93f77a4fbcd3
Create Date: 2026-05-13 14:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5b0f8d4a7c21"
down_revision: Union[str, Sequence[str], None] = "93f77a4fbcd3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DOG_TABLE = "dog_friendly_places"
VET_TABLE = "vet_clinics"


def _has_columns(table_name: str, expected_columns: set[str]) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return False
    actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
    return expected_columns.issubset(actual_columns)


def _backup_table(table_name: str, backup_table_name: str) -> None:
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF to_regclass('{table_name}') IS NOT NULL
                   AND to_regclass('{backup_table_name}') IS NULL THEN
                    EXECUTE 'CREATE TABLE {backup_table_name} AS TABLE {table_name} WITH DATA';
                END IF;
            END $$;
            """
        )
    )


def _recreate_dog_friendly_places() -> None:
    current_columns = {
        "id",
        "dogfriendly_place_name",
        "dogfriendly_place_city",
        "dogfriendly_place_street",
        "dogfriendly_place_building_number",
        "dogfriendly_place_lat",
        "dogfriendly_place_lon",
        "dogfriendly_place_geocoder_precision",
        "dogfriendly_place_working_hours",
        "dogfriendly_place_is_24_7",
        "dogfriendly_place_status",
        "dogfriendly_place_last_verified",
    }
    if _has_columns(DOG_TABLE, current_columns):
        return

    _backup_table(DOG_TABLE, "dog_friendly_places_legacy_backup")
    op.execute("DROP TABLE IF EXISTS dog_friendly_places CASCADE")
    op.create_table(
        DOG_TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dogfriendly_place_name", sa.String(length=50), nullable=False),
        sa.Column("dogfriendly_place_city", sa.String(length=50), nullable=False),
        sa.Column("dogfriendly_place_street", sa.String(length=127), nullable=False),
        sa.Column("dogfriendly_place_building_number", sa.String(length=20), nullable=False),
        sa.Column("dogfriendly_place_lat", sa.Numeric(), nullable=False),
        sa.Column("dogfriendly_place_lon", sa.Numeric(), nullable=False),
        sa.Column("dogfriendly_place_geocoder_precision", sa.String(length=50), nullable=False),
        sa.Column("dogfriendly_place_working_hours", sa.String(length=255), nullable=False),
        sa.Column("dogfriendly_place_is_24_7", sa.Boolean(), nullable=False),
        sa.Column("dogfriendly_place_status", sa.String(length=20), nullable=False),
        sa.Column(
            "dogfriendly_place_last_verified",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dogfriendly_place_name",
            "dogfriendly_place_city",
            "dogfriendly_place_street",
            "dogfriendly_place_building_number",
            name="unique_dog_friendly_place",
        ),
    )


def _recreate_vet_clinics() -> None:
    current_columns = {
        "id",
        "vet_name",
        "vet_city",
        "vet_street",
        "vet_building_number",
        "vet_lat",
        "vet_lon",
        "vet_geocoder_precision",
        "vet_working_hours",
        "vet_is_24_7",
        "vet_status",
        "vet_phone",
        "vet_website",
        "vet_last_verified",
    }
    if _has_columns(VET_TABLE, current_columns):
        return

    _backup_table(VET_TABLE, "vet_clinics_legacy_backup")
    op.execute("DROP TABLE IF EXISTS vet_clinics CASCADE")
    op.create_table(
        VET_TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vet_name", sa.String(length=50), nullable=False),
        sa.Column("vet_city", sa.String(length=50), nullable=False),
        sa.Column("vet_street", sa.String(length=127), nullable=False),
        sa.Column("vet_building_number", sa.String(length=20), nullable=False),
        sa.Column("vet_lat", sa.Numeric(), nullable=False),
        sa.Column("vet_lon", sa.Numeric(), nullable=False),
        sa.Column("vet_geocoder_precision", sa.String(length=50), nullable=False),
        sa.Column("vet_working_hours", sa.String(length=255), nullable=False),
        sa.Column("vet_is_24_7", sa.Boolean(), nullable=False),
        sa.Column("vet_status", sa.String(length=20), nullable=False),
        sa.Column("vet_phone", sa.String(length=16), nullable=True),
        sa.Column("vet_website", sa.Text(), nullable=True),
        sa.Column(
            "vet_last_verified",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "vet_name",
            "vet_city",
            "vet_street",
            "vet_building_number",
            name="unique_vet_clinic",
        ),
    )


def upgrade() -> None:
    _recreate_dog_friendly_places()
    _recreate_vet_clinics()


def downgrade() -> None:
    pass
