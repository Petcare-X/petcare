"""make dog animal type id first

Revision ID: 2f6b8c1d4e9a
Revises: 1d7f3c8b9a2e
Create Date: 2026-04-08 13:30:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2f6b8c1d4e9a"
down_revision: Union[str, Sequence[str], None] = "1d7f3c8b9a2e"
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
            current_first_id integer;
            temp_id integer := 1000001;
        BEGIN
            SELECT id INTO dog_id
            FROM animals_types
            WHERE lower(animal_name) LIKE 'dog%'
               OR lower(animal_name) LIKE 'собак%';

            IF dog_id IS NULL THEN
                RAISE EXCEPTION 'Dog animal type was not found';
            END IF;

            IF dog_id = 1 THEN
                SELECT MIN(id) INTO current_first_id FROM animals_types;
                IF dog_id = current_first_id THEN
                    RETURN;
                END IF;
            END IF;

            SELECT MIN(id) INTO current_first_id
            FROM animals_types;

            IF current_first_id IS NULL THEN
                RAISE EXCEPTION 'No animal types were found';
            END IF;

            SET CONSTRAINTS pets_info_animal_type_id_fkey DEFERRED;
            SET CONSTRAINTS fk_animals_breeds_animal_type_id DEFERRED;

            UPDATE animals_types
            SET id = temp_id
            WHERE id = dog_id;

            UPDATE pets_info
            SET animal_type_id = temp_id
            WHERE animal_type_id = dog_id;

            UPDATE animals_breeds
            SET animal_type_id = temp_id
            WHERE animal_type_id = dog_id;

            UPDATE animals_types
            SET id = dog_id
            WHERE id = current_first_id;

            UPDATE pets_info
            SET animal_type_id = dog_id
            WHERE animal_type_id = current_first_id;

            UPDATE animals_breeds
            SET animal_type_id = dog_id
            WHERE animal_type_id = current_first_id;

            UPDATE animals_types
            SET id = 1
            WHERE id = temp_id AND current_first_id = 1;

            UPDATE animals_types
            SET id = current_first_id
            WHERE id = temp_id AND current_first_id <> 1;

            UPDATE pets_info
            SET animal_type_id = current_first_id
            WHERE animal_type_id = temp_id;

            UPDATE animals_breeds
            SET animal_type_id = current_first_id
            WHERE animal_type_id = temp_id;
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
            next_id integer;
            temp_id integer := 1000001;
        BEGIN
            SELECT id INTO dog_id
            FROM animals_types
            WHERE lower(animal_name) LIKE 'dog%'
               OR lower(animal_name) LIKE 'собак%';

            IF dog_id IS NULL THEN
                RAISE EXCEPTION 'Dog animal type was not found';
            END IF;

            SELECT MIN(id) INTO next_id
            FROM animals_types
            WHERE id > dog_id;

            IF next_id IS NULL THEN
                RETURN;
            END IF;

            SET CONSTRAINTS pets_info_animal_type_id_fkey DEFERRED;
            SET CONSTRAINTS fk_animals_breeds_animal_type_id DEFERRED;

            UPDATE animals_types
            SET id = temp_id
            WHERE id = 1;

            UPDATE pets_info
            SET animal_type_id = temp_id
            WHERE animal_type_id = 1;

            UPDATE animals_breeds
            SET animal_type_id = temp_id
            WHERE animal_type_id = 1;

            UPDATE animals_types
            SET id = dog_id
            WHERE id = next_id;

            UPDATE pets_info
            SET animal_type_id = dog_id
            WHERE animal_type_id = next_id;

            UPDATE animals_breeds
            SET animal_type_id = dog_id
            WHERE animal_type_id = next_id;

            UPDATE animals_types
            SET id = next_id
            WHERE id = temp_id;

            UPDATE pets_info
            SET animal_type_id = next_id
            WHERE animal_type_id = temp_id;

            UPDATE animals_breeds
            SET animal_type_id = next_id
            WHERE animal_type_id = temp_id;
        END $$;
        """
    )
