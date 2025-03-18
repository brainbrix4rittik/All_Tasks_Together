# app/models.py
from sqlalchemy.orm import validates
from .database import Base

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    # Add fields for soft delete functionality
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    @validates('title')
    def validate_title(self, key, title):
        assert len(title) > 0, 'Title must not be empty'
        return title