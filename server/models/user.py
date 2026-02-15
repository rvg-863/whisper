import uuid
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from server.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    identity_key_public: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signed_prekey_public: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signed_prekey_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    one_time_prekeys: Mapped[Optional[dict]] = mapped_column(JSONB, default=list, nullable=True)
