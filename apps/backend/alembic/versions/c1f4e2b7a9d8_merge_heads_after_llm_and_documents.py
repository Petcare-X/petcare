"""merge llm and documents heads

Revision ID: c1f4e2b7a9d8
Revises: 6d5f2e7b1c4a, ab3d7f2c9e41
Create Date: 2026-03-25 18:30:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "c1f4e2b7a9d8"
down_revision: Union[str, Sequence[str], None] = ("6d5f2e7b1c4a", "ab3d7f2c9e41")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge revision with no schema changes."""


def downgrade() -> None:
    """Split merge revision with no schema changes."""
