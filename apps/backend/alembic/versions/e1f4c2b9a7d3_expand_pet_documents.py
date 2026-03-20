"""expand pet_documents for storage metadata

Revision ID: e1f4c2b9a7d3
Revises: a6c1e8b6d2f4
Create Date: 2026-03-20 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1f4c2b9a7d3"
down_revision: Union[str, Sequence[str], None] = "a6c1e8b6d2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "pet_documents",
        "custom_document_name",
        new_column_name="custom_document_name_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )

    op.drop_constraint(
        "pet_documents_custom_document_name_fkey",
        "pet_documents",
        type_="foreignkey",
    )
    op.alter_column(
        "pet_documents",
        "custom_document_name_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_foreign_key(
        "pet_documents_custom_document_name_id_fkey",
        "pet_documents",
        "custom_documents_names",
        ["custom_document_name_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("pet_documents", sa.Column("object_key", sa.Text(), nullable=True))
    op.add_column("pet_documents", sa.Column("original_filename", sa.String(length=255), nullable=True))
    op.add_column("pet_documents", sa.Column("content_type", sa.String(length=100), nullable=True))
    op.add_column("pet_documents", sa.Column("size_bytes", sa.BIGINT(), nullable=True))
    op.add_column("pet_documents", sa.Column("etag", sa.String(length=128), nullable=True))
    op.add_column("pet_documents", sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True))

    op.create_unique_constraint(
        "uq_pet_documents_object_key",
        "pet_documents",
        ["object_key"],
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pet_documents) THEN
                ALTER TABLE pet_documents
                ALTER COLUMN object_key SET NOT NULL;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.drop_constraint("uq_pet_documents_object_key", "pet_documents", type_="unique")

    op.drop_column("pet_documents", "uploaded_at")
    op.drop_column("pet_documents", "etag")
    op.drop_column("pet_documents", "size_bytes")
    op.drop_column("pet_documents", "content_type")
    op.drop_column("pet_documents", "original_filename")
    op.drop_column("pet_documents", "object_key")

    op.drop_constraint(
        "pet_documents_custom_document_name_id_fkey",
        "pet_documents",
        type_="foreignkey",
    )
    op.execute(
        """
        UPDATE pet_documents
        SET custom_document_name_id = 1
        WHERE custom_document_name_id IS NULL
        """
    )
    op.alter_column(
        "pet_documents",
        "custom_document_name_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "pet_documents_custom_document_name_fkey",
        "pet_documents",
        "custom_documents_names",
        ["custom_document_name_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "pet_documents",
        "custom_document_name_id",
        new_column_name="custom_document_name",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )