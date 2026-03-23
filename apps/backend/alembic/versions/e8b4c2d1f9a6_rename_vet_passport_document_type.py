"""rename vet passport document type

Revision ID: e8b4c2d1f9a6
Revises: d4c8e1a9b2f7
Create Date: 2026-03-23 19:30:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e8b4c2d1f9a6"
down_revision: Union[str, Sequence[str], None] = "d4c8e1a9b2f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_NAME = "Вет паспорт"
NEW_NAME = "Ветиринарный паспорт"


def upgrade() -> None:
    old_name = OLD_NAME.replace("'", "''")
    new_name = NEW_NAME.replace("'", "''")
    op.execute(
        f"""
        UPDATE documents_types
        SET document_name = '{new_name}'
        WHERE document_name = '{old_name}';
        """
    )


def downgrade() -> None:
    old_name = OLD_NAME.replace("'", "''")
    new_name = NEW_NAME.replace("'", "''")
    op.execute(
        f"""
        UPDATE documents_types
        SET document_name = '{old_name}'
        WHERE document_name = '{new_name}';
        """
    )
