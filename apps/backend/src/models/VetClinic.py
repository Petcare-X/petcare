from sqlalchemy import String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class VetClinic(Base):
    __tablename__ = "vet_clinics"
    
    id: Mapped[int_primary_key]
    vet_clinic_name: Mapped[str] = mapped_column(String(50))
    vet_clinic_address: Mapped[str] = mapped_column(String(50))
    vet_clinic_rating: Mapped[int] = mapped_column(Numeric)
    vet_clinic_work_hours: Mapped[str] = mapped_column(String(50))
    vet_clinic_contacts: Mapped[str] = mapped_column(String(50))
    vet_clinic_description: Mapped[str] = mapped_column(Text)
    vet_clinic_photo: Mapped[str] = mapped_column(Text)