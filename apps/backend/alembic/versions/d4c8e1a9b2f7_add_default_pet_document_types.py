"""add default pet document types

Revision ID: d4c8e1a9b2f7
Revises: f2a1b6c4d9e8
Create Date: 2026-03-23 19:05:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d4c8e1a9b2f7"
down_revision: Union[str, Sequence[str], None] = "f2a1b6c4d9e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DOCUMENT_TYPES = (
    "Вет паспорт",
    "Вакцинация",
    "Анализы",
    "Заключения",
    "Родословная",
)


def upgrade() -> None:
    for document_name in DOCUMENT_TYPES:
        escaped_name = document_name.replace("'", "''")
        op.execute(
            f"""
            INSERT INTO documents_types (document_name)
            SELECT '{escaped_name}'
            WHERE NOT EXISTS (
                SELECT 1
                FROM documents_types
                WHERE document_name = '{escaped_name}'
            );
            """
        )


def downgrade() -> None:
    for document_name in DOCUMENT_TYPES:
        escaped_name = document_name.replace("'", "''")
        op.execute(
            f"""
            DELETE FROM documents_types
            WHERE document_name = '{escaped_name}'
              AND NOT EXISTS (
                  SELECT 1
                  FROM pet_documents
                  WHERE pet_documents.document_id = documents_types.id
              );
            """
        )
