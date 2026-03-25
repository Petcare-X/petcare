"""fix llm messages chat foreign key

Revision ID: 6d5f2e7b1c4a
Revises: 55e00d599145
Create Date: 2026-03-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d5f2e7b1c4a"
down_revision: Union[str, Sequence[str], None] = "55e00d599145"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = inspector.get_foreign_keys("llm_chats_messages")

    for foreign_key in foreign_keys:
        constrained_columns = foreign_key.get("constrained_columns") or []
        referred_table = foreign_key.get("referred_table")
        constraint_name = foreign_key.get("name")
        if constrained_columns == ["chat_id"] and referred_table != "llm_chats" and constraint_name:
            op.drop_constraint(constraint_name, "llm_chats_messages", type_="foreignkey")

    current_foreign_keys = sa.inspect(bind).get_foreign_keys("llm_chats_messages")
    has_correct_fk = any(
        (fk.get("constrained_columns") or []) == ["chat_id"]
        and fk.get("referred_table") == "llm_chats"
        for fk in current_foreign_keys
    )
    if not has_correct_fk:
        op.create_foreign_key(
            "fk_llm_chats_messages_chat_id_llm_chats",
            "llm_chats_messages",
            "llm_chats",
            ["chat_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE llm_chats_messages
        DROP CONSTRAINT IF EXISTS fk_llm_chats_messages_chat_id_llm_chats
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conrelid = 'llm_chats_messages'::regclass
                  AND conname = 'fk_llm_chats_messages_chat_id_llm_chats_messages'
            ) THEN
                ALTER TABLE llm_chats_messages
                ADD CONSTRAINT fk_llm_chats_messages_chat_id_llm_chats_messages
                FOREIGN KEY (chat_id)
                REFERENCES llm_chats_messages(id)
                ON DELETE CASCADE;
            END IF;
        END
        $$;
        """
    )
