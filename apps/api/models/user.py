from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.database import Base

# Association table for user integrations
user_integrations = Table(
    "user_integrations",
    Base.metadata,
    Column("user_id", PGUUID, ForeignKey("users.id"), primary_key=True),
    Column("provider", String, primary_key=True),
    Column("external_id", String, nullable=False),
    Column("access_token", String, nullable=False),
    Column("refresh_token", String),
    Column("expires_at", DateTime),
    Column("scopes", ARRAY(String)),
    Column("metadata", JSONB),
)

class User(Base):
    """User model for authentication and profile data."""
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Profile data
    display_name: Mapped[str | None] = mapped_column(String)
    bio: Mapped[str | None] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    avatar_url: Mapped[str | None] = mapped_column(String)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Relationships
    activities = relationship("Activity", back_populates="user")
    narratives = relationship("Narrative", back_populates="user")
    newsletters = relationship("Newsletter", back_populates="user")
    matches = relationship(
        "Match",
        foreign_keys="Match.user_id",
        back_populates="user",
    )
    matched_by = relationship(
        "Match",
        foreign_keys="Match.matched_user_id",
        back_populates="matched_user",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>" 