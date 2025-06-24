"""
SQLAlchemy Models for Authentication Domain.
Maps to existing Supabase auth.users table (READ-ONLY).
"""

from sqlalchemy import (
    Column,
    ColumnElement,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Any, Literal, Optional
import uuid

from sqlalchemy.orm.relationships import Relationship

from core.config import settings

# Create base class for models
Base = declarative_base()


class User(Base):
    """
    SQLAlchemy model mapping to Supabase auth.users table.
    READ-ONLY - User creation happens through Supabase Auth API only.
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    # Primary key - UUID from Supabase
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core user fields from Supabase auth.users
    email = Column(
        String(settings.DB_EMAIL_MAX_LENGTH), unique=True, nullable=False, index=True
    )
    encrypted_password = Column(
        String(settings.DB_PASSWORD_MAX_LENGTH), nullable=True
    )  # Handled by Supabase
    email_confirmed_at = Column(DateTime, nullable=True)
    invited_at = Column(DateTime, nullable=True)
    confirmation_token = Column(String(settings.DB_TOKEN_MAX_LENGTH), nullable=True)
    confirmation_sent_at = Column(DateTime, nullable=True)
    recovery_token = Column(String(settings.DB_TOKEN_MAX_LENGTH), nullable=True)
    recovery_sent_at = Column(DateTime, nullable=True)
    email_change_token_new = Column(String(settings.DB_TOKEN_MAX_LENGTH), nullable=True)
    email_change = Column(String(settings.DB_EMAIL_MAX_LENGTH), nullable=True)
    email_change_sent_at = Column(DateTime, nullable=True)
    last_sign_in_at = Column(DateTime, nullable=True)
    raw_app_meta_data = Column(Text, nullable=True)
    raw_user_meta_data = Column(Text, nullable=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    phone = Column(String(settings.DB_PHONE_MAX_LENGTH), nullable=True)
    phone_confirmed_at = Column(DateTime, nullable=True)
    phone_change = Column(String(settings.DB_PHONE_MAX_LENGTH), nullable=True)
    phone_change_token = Column(String(settings.DB_TOKEN_MAX_LENGTH), nullable=True)
    phone_change_sent_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    email_change_token_current = Column(
        String(settings.DB_TOKEN_MAX_LENGTH), nullable=True
    )
    email_change_confirm_status = Column(
        String(settings.DB_STATUS_CODE_LENGTH), nullable=True
    )
    banned_until = Column(DateTime, nullable=True)
    reauthentication_token = Column(String(settings.DB_TOKEN_MAX_LENGTH), nullable=True)
    reauthentication_sent_at = Column(DateTime, nullable=True)
    is_sso_user = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship to user profile
    profile: Relationship[Any] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def is_active(self) -> bool:
        """Check if user is active (confirmed and not banned)."""
        # Convert SQLAlchemy expressions to Python booleans for type safety
        email_confirmed: bool = self.email_confirmed_at is not None
        not_deleted: bool = self.deleted_at is None
        not_banned: bool = (
            self.banned_until is None or self.banned_until < datetime.utcnow()
        )

        return bool(email_confirmed and not_deleted and not_banned)

    def is_verified(self) -> bool:
        """Check if user email is verified."""
        return self.email_confirmed_at is not None

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base):
    """
    Extended user profile data stored in our application schema.
    Links to Supabase auth.users via user_id foreign key.
    """

    __tablename__: str = "user_profiles"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to auth.users.id
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Profile fields
    display_name = Column(String(settings.DB_DISPLAY_NAME_MAX_LENGTH), nullable=True)
    first_name = Column(String(settings.DB_FIRST_NAME_MAX_LENGTH), nullable=True)
    last_name = Column(String(settings.DB_LAST_NAME_MAX_LENGTH), nullable=True)
    avatar_url = Column(String(settings.DB_URL_MAX_LENGTH), nullable=True)
    bio = Column(Text, nullable=True)

    # Preferences as JSON text (could be upgraded to JSONB later)
    preferences = Column(Text, nullable=True)  # JSON string for user preferences

    # App-specific fields
    timezone = Column(String(settings.DB_TIMEZONE_MAX_LENGTH), default="UTC")
    language = Column(String(settings.DB_LANGUAGE_CODE_LENGTH), default="en")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship back to user
    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, display_name={self.display_name})>"


# Export models for easy importing
__all__ = ["User", "UserProfile", "Base"]
