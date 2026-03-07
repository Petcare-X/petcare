from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class DocumentType(Base):
    __tablename__ = "documents_types"
    
    id: Mapped[int_primary_key]
    document_name: Mapped[str] = mapped_column(String(50), unique=True)
    