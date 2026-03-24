"""restore custom_name in pet_documents

Revision ID: ab3d7f2c9e41
Revises: e8b4c2d1f9a6
Create Date: 2026-03-24 12:10:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ab3d7f2c9e41"
down_revision: Union[str, Sequence[str], None] = "e8b4c2d1f9a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'pet_documents'
                  AND column_name = 'custom_name'
            ) THEN
                ALTER TABLE pet_documents
                ADD COLUMN custom_name VARCHAR(255);
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        UPDATE pet_documents
        SET custom_name = regexp_replace(split_part(object_key, '/', array_length(string_to_array(object_key, '/'), 1)), '\\.[^.]+$', '')
        WHERE custom_name IS NULL OR custom_name = '';
        """
    )
    op.execute(
        """
        ALTER TABLE pet_documents
        ALTER COLUMN custom_name SET NOT NULL;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'pet_documents'
                  AND column_name = 'original_name'
            ) THEN
                ALTER TABLE pet_documents DROP COLUMN original_name;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'pet_documents'
                  AND column_name = 'original_name'
            ) THEN
                ALTER TABLE pet_documents
                ADD COLUMN original_name VARCHAR(255);
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        UPDATE pet_documents
        SET original_name = custom_name
        WHERE custom_name IS NOT NULL;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'pet_documents'
                  AND column_name = 'custom_name'
            ) THEN
                ALTER TABLE pet_documents DROP COLUMN custom_name;
            END IF;
        END
        $$;
        """
    )
