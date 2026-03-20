"""align schema with current sqlalchemy models

Revision ID: a6c1e8b6d2f4
Revises: 4b0d8f89c1e9
Create Date: 2026-03-18 16:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6c1e8b6d2f4"
down_revision: Union[str, Sequence[str], None] = "4b0d8f89c1e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # animals_breeds: animal_breed_name -> animal_breed
    op.alter_column("animals_breeds", "animal_breed_name", new_column_name="animal_breed")

    # users_info: user_phone -> user_phone_number
    op.alter_column("users_info", "user_phone", new_column_name="user_phone_number")
    op.drop_index("ix_users_info_user_phone", table_name="users_info")
    op.create_index(
        "ix_users_info_user_phone_number",
        "users_info",
        ["user_phone_number"],
        unique=True,
    )

    # pets_info: align names/types with model
    op.execute("ALTER TABLE pets_info DROP CONSTRAINT IF EXISTS pets_info_pet_pedigree_fkey")
    op.alter_column("pets_info", "pet_type", new_column_name="animal_type_id")
    op.alter_column("pets_info", "pet_breed", new_column_name="animal_breed_id")
    op.alter_column("pets_info", "pet_pedigree", new_column_name="pedigree")
    op.alter_column(
        "pets_info",
        "pedigree",
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        postgresql_using="CASE WHEN pedigree IS NULL THEN NULL ELSE pedigree <> 0 END",
    )

    op.add_column("pets_info", sa.Column("pet_weight", sa.Numeric(), nullable=True))
    op.execute("UPDATE pets_info SET pet_weight = 0 WHERE pet_weight IS NULL")
    op.alter_column("pets_info", "pet_weight", nullable=False)

    # shared_users: sharing_end can be NULL in model
    op.alter_column("shared_users", "sharing_end", existing_type=sa.DateTime(timezone=True), nullable=True)

    # no model for animals_pedigrees anymore
    op.drop_table("animals_pedigrees")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "animals_pedigrees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("animal_pedigree", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("animal_pedigree"),
    )

    op.execute("UPDATE shared_users SET sharing_end = NOW() WHERE sharing_end IS NULL")
    op.alter_column("shared_users", "sharing_end", existing_type=sa.DateTime(timezone=True), nullable=False)

    op.drop_column("pets_info", "pet_weight")

    op.alter_column(
        "pets_info",
        "pedigree",
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        postgresql_using="CASE WHEN pedigree THEN 1 ELSE 0 END",
    )
    op.alter_column("pets_info", "pedigree", new_column_name="pet_pedigree")
    op.alter_column("pets_info", "animal_breed_id", new_column_name="pet_breed")
    op.alter_column("pets_info", "animal_type_id", new_column_name="pet_type")
    op.create_foreign_key(
        "pets_info_pet_pedigree_fkey",
        "pets_info",
        "animals_pedigrees",
        ["pet_pedigree"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_index("ix_users_info_user_phone_number", table_name="users_info")
    op.alter_column("users_info", "user_phone_number", new_column_name="user_phone")
    op.create_index("ix_users_info_user_phone", "users_info", ["user_phone"], unique=True)

    op.alter_column("animals_breeds", "animal_breed", new_column_name="animal_breed_name")
