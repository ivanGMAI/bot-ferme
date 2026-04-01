import uuid
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, IdUuidPkMixin
from features.users.schemas.enums import UserDomain, Environment


class User(IdUuidPkMixin, Base):
    login: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    env: Mapped[Environment] = mapped_column(String(50), index=True)
    domain: Mapped[UserDomain] = mapped_column(String(50), index=True)

    locktime: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
