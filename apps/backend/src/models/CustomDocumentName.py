from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class CustomDocumentName(Base):
    __tablename__ = "custom_documents_names"
    
    id: Mapped[int_primary_key]
    name: Mapped[str] = mapped_column(String(50), unique=True)
