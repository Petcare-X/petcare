from sqlalchemy import BIGINT, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

from datetime import datetime

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class PetDocument(Base):
    __tablename__ = "pet_documents"

    id: Mapped[int_primary_key]
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents_types.id", ondelete="CASCADE"))
    custom_document_name_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("custom_documents_names.id", ondelete="SET NULL"),
        nullable=True,
    )
    object_key: Mapped[str] = mapped_column(Text, unique=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BIGINT, nullable=True)
    etag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)