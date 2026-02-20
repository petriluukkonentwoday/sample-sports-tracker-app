"""Friendship model for social features."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.connection import Base


class Friendship(Base):
    """User friendship / follow relationship."""

    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="unique_friendship"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    friend_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, accepted, blocked

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Friendship {self.user_id} -> {self.friend_id} ({self.status})>"
