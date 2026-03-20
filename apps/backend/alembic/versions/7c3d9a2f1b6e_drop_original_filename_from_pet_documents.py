"""drop original_filename from pet_documents

Revision ID: 7c3d9a2f1b6e
Revises: e1f4c2b9a7d3
Create Date: 2026-03-20 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c3d9a2f1b6e"
down_revision: Union[str, Sequence[str], None] = "e1f4c2b9a7d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'pet_documents'
                  AND column_name = 'original_filename'
            ) THEN
                ALTER TABLE pet_documents DROP COLUMN original_filename;
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
                  AND column_name = 'original_filename'
            ) THEN
                ALTER TABLE pet_documents
                ADD COLUMN original_filename VARCHAR(255);
            END IF;
        END
        $$;
        """
    )