from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer

# Create base class for models
Base = declarative_base()


class PantryItem(Base):
    """
    SQLAlchemy model mapping to Supabase public.pantry table.
    """

    __table_args__: str = "public"
    __tablename__: dict[str, str] = {"schema": "pantry"}

    # Primary key - UUID from Supabase
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core pantry fields from Supabase
    ingredient_id = (
        UUID  # ingredient_id UUID REFERENCES IngredientMaster(ingredient_id)
    )
    user_id = UUID  # user_id UUID REFERENCES "user"(user_id)
    quantity = Column(Integer(), nullable=False)  # in g
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
