"""link animal breeds to types

Revision ID: 1d7f3c8b9a2e
Revises: 8c4f1b7d2e6a
Create Date: 2026-04-08 13:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "1d7f3c8b9a2e"
down_revision: Union[str, Sequence[str], None] = "8c4f1b7d2e6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("animals_breeds", sa.Column("animal_type_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_animals_breeds_animal_type_id",
        "animals_breeds",
        "animals_types",
        ["animal_type_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE animals_breeds AS breed
        SET animal_type_id = mapping.animal_type_id
        FROM (
            SELECT animal_breed_id, MIN(animal_type_id) AS animal_type_id
            FROM pets_info
            GROUP BY animal_breed_id
            HAVING COUNT(DISTINCT animal_type_id) = 1
        ) AS mapping
        WHERE mapping.animal_breed_id = breed.id;
        """
    )
    op.execute(
        """
        UPDATE animals_breeds AS breed
        SET animal_type_id = animal_type.id
        FROM animals_types AS animal_type
        WHERE breed.animal_type_id IS NULL
          AND lower(breed.animal_breed) IN ('немецкая овчарка', 'французский бульдог')
          AND (
              lower(animal_type.animal_name) LIKE 'dog%%'
              OR lower(animal_type.animal_name) LIKE 'собак%%'
          );
        """
    )
    op.execute(
        """
        DO $$
        DECLARE
            unresolved_count integer;
            unresolved_breeds text;
        BEGIN
            SELECT COUNT(*) INTO unresolved_count
            FROM animals_breeds
            WHERE animal_type_id IS NULL;

            IF unresolved_count > 0 THEN
                SELECT string_agg(format('%s:%s', id, animal_breed), ', ' ORDER BY id)
                INTO unresolved_breeds
                FROM animals_breeds
                WHERE animal_type_id IS NULL;

                RAISE EXCEPTION 'Cannot infer animal_type_id for all breeds. Unresolved breeds: %', unresolved_breeds;
            END IF;
        END $$;
        """
    )
    op.alter_column("animals_breeds", "animal_type_id", nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_animals_breeds_animal_type_id", "animals_breeds", type_="foreignkey")
    op.drop_column("animals_breeds", "animal_type_id")
