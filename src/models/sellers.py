from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from .base import BaseModel
from typing import Optional

class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    books = relationship('Book', back_populates='seller', cascade="all, delete-orphan")

    #books: Mapped[Optional[list[Book]]] = relationship()