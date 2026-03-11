from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class CustomDocumentName(Base):
    __tablename__ = "custom_documents_names"
    
    id: Mapped[int_primary_key]
    name: Mapped[int] = mapped_column(Integer (50), unique=True)