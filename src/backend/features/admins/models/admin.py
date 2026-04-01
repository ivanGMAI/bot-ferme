from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, IdUuidPkMixin


class Admin(IdUuidPkMixin, Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
