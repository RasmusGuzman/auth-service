from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import CITEXT
from .database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import Optional

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[str]