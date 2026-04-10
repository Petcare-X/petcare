"""force dog animal type id to 1

Revision ID: 3a7d1e5c9b2f
Revises: 2f6b8c1d4e9a
Create Date: 2026-04-08 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3a7d1e5c9b2f"
down_revision: Union[str, Sequence[str], None] = "2f6b8c1d4e9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE pets_info
        ALTER CONSTRAINT pets_info_animal_type_id_fkey DEFERRABLE INITIALLY DEFERRED;
        """
    )
    op.execute(
        """
        ALTER TABLE animals_breeds
        ALTER CONSTRAINT fk_animals_breeds_animal_type_id DEFERRABLE INITIALLY DEFERRED;
        """
    )
    op.execute(
        """
        DO $$
        DECLARE
            dog_id integer;
            first_id_exists boolean;
            temp_id integer := 1000002;
        BEGIN
            SELECT id INTO dog_id
            FROM animals_types
            WHERE lower(animal_name) LIKE 'dog%'
               OR lower(animal_name) LIKE 'собак%';

            IF dog_id IS NULL THEN
                RAISE EXCEPTION 'Dog animal type was not found';
            END IF;

            IF dog_id = 1 THEN
                RETURN;
            END IF;

            SELECT EXISTS(SELECT 1 FROM animals_types WHERE id = 1) INTO first_id_exists;

            SET CONSTRAINTS pets_info_animal_type_id_fkey DEFERRED;
            SET CONSTRAINTS fk_animals_breeds_animal_type_id DEFERRED;

            IF first_id_exists THEN
                UPDATE animals_types
                SET id = temp_id
                WHERE id = 1;

                UPDATE pets_info
                SET animal_type_id = temp_id
                WHERE animal_type_id = 1;

                UPDATE animals_breeds
                SET animal_type_id = temp_id
                WHERE animal_type_id = 1;
            END IF;

            UPDATE animals_types
            SET id = 1
            WHERE id = dog_id;

            UPDATE pets_info
            SET animal_type_id = 1
            WHERE animal_type_id = dog_id;

            UPDATE animals_breeds
            SET animal_type_id = 1
            WHERE animal_type_id = dog_id;

            IF first_id_exists THEN
                UPDATE animals_types
                SET id = dog_id
                WHERE id = temp_id;

                UPDATE pets_info
                SET animal_type_id = dog_id
                WHERE animal_type_id = temp_id;

                UPDATE animals_breeds
                SET animal_type_id = dog_id
                WHERE animal_type_id = temp_id;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE pets_info
        ALTER CONSTRAINT pets_info_animal_type_id_fkey DEFERRABLE INITIALLY DEFERRED;
        """
    )
    op.execute(
        """
        ALTER TABLE animals_breeds
        ALTER CONSTRAINT fk_animals_breeds_animal_type_id DEFERRABLE INITIALLY DEFERRED;
        """
    )
    op.execute(
        """
        DO $$
        DECLARE
            dog_id integer;
            second_id_exists boolean;
            temp_id integer := 1000002;
        BEGIN
            SELECT id INTO dog_id
            FROM animals_types
            WHERE lower(animal_name) LIKE 'dog%'
               OR lower(animal_name) LIKE 'собак%';

            IF dog_id IS NULL OR dog_id <> 1 THEN
                RETURN;
            END IF;

            SELECT EXISTS(SELECT 1 FROM animals_types WHERE id = 2) INTO second_id_exists;

            SET CONSTRAINTS pets_info_animal_type_id_fkey DEFERRED;
            SET CONSTRAINTS fk_animals_breeds_animal_type_id DEFERRED;

            IF second_id_exists THEN
                UPDATE animals_types
                SET id = temp_id
                WHERE id = 2;

                UPDATE pets_info
                SET animal_type_id = temp_id
                WHERE animal_type_id = 2;

                UPDATE animals_breeds
                SET animal_type_id = temp_id
                WHERE animal_type_id = 2;
            END IF;

            UPDATE animals_types
            SET id = 2
            WHERE id = 1;

            UPDATE pets_info
            SET animal_type_id = 2
            WHERE animal_type_id = 1;

            UPDATE animals_breeds
            SET animal_type_id = 2
            WHERE animal_type_id = 1;

            IF second_id_exists THEN
                UPDATE animals_types
                SET id = 1
                WHERE id = temp_id;

                UPDATE pets_info
                SET animal_type_id = 1
                WHERE animal_type_id = temp_id;

                UPDATE animals_breeds
                SET animal_type_id = 1
                WHERE animal_type_id = temp_id;
            END IF;
        END $$;
        """
    )
