from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PantryItem(Base):
    __tablename__: str = "items"
    __table_args__: dict[str, str] = {"schema": "pantry"}

    id: int = Column(String, primary_key=True)
    name: str = Column(String, nullable=False)
    unit: str = Column(String, nullable=False)
    quantity: float = Column(String, nullable=False)
    expiration_date: DateTime = Column(DateTime, nullable=True)
    created_at: DateTime = Column(DateTime, default=DateTime.utcnow, nullable=False)
    updated_at: DateTime = Column(DateTime, default=DateTime.utcnow, onupdate=DateTime.utcnow, nullable=False)

class PantryCategory(Base):
    __tablename__: str = "categories"
    __table_args__: dict[str, str] = {"schema": "pantry"}

    id: int = Column(String, primary_key=True)
    name: str = Column(String, nullable=False)
    description: str = Column(Text, nullable=True)
    created_at: DateTime = Column(DateTime, default=DateTime.utcnow, nullable=False)
    updated_at: DateTime = Column(DateTime, default=DateTime.utcnow, onupdate=DateTime.utcnow, nullable=False)

    items = relationship("PantryItem", backref="category")