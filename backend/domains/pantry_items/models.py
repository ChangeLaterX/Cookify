"""
SQLAlchemy Models for Pantry Items Domain.
Defines the data structure for user pantry management.
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

from core.config import settings

# Use the same base as auth models
Base = declarative_base()


class PantryItem(Base):
    """
    SQLAlchemy model for pantry items.
    Maps to the public.pantry_items table.
    Represents ingredients that users currently have in their pantry.
    """

    __tablename__ = "pantry_items"
    __table_args__ = {"schema": "public"}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to auth.users
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("auth.users.id"), 
        nullable=False,
        index=True
    )
    
    # Item details
    name = Column(Text, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(Text, nullable=False)
    category = Column(Text, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # Foreign key to ingredient_master
    ingredient_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("ingredient_master.ingredient_id"), 
        nullable=False,
        index=True
    )
    
    # Timestamps
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PantryItem(id={self.id}, user_id={self.user_id}, name='{self.name}', quantity={self.quantity} {self.unit})>"

    def to_dict(self) -> dict:
        """Convert PantryItem instance to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "category": self.category,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "added_at": self.added_at.isoformat(),
            "ingredient_id": self.ingredient_id,
        }
