"""fix veterinary passport spelling

Revision ID: f4b2c8d1e6a3
Revises: c1f4e2b7a9d8
Create Date: 2026-03-25 19:10:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f4b2c8d1e6a3"
down_revision: Union[str, Sequence[str], None] = "c1f4e2b7a9d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_NAME = "Ветиринарный паспорт"
NEW_NAME = "Ветеринарный паспорт"


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
