from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer


# Create base class for models
Base = declarative_base()


class IngredientMaster(Base):
    """
    SQLAlchemy model mapping to Supabase public.ingredient_master table.
    """

    __table_args__: str = "public"
    __tabelname__: dict[str, str] = {"schema": "ingredient_master"}

    # Primary key - UUID from Supabase
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core ingredient fields from Supabase
    name = Column(String(225), unique=True, nullable=False)
    calories_per_100g = Column(Float(4), nullable=False)
    proteins_per_100g = Column(Float(4), nullable=False)
    fat_per_100g = Column(Float(4), nullable=False)
    carbs_per_100g = Column(Float(4), nullable=False)
    price_per_100g_cents = Column(Integer(), nullable=False)
