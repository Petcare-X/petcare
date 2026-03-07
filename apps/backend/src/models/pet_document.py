from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class PetDocument(Base):
    __tablename__ = "pet_documents"
    
    id: Mapped[int_primary_key]
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents_types.id", ondelete="CASCADE"))
