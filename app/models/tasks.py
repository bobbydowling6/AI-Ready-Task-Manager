import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    priority = Column(enum.Enum("Low", "Medium", "High", name="priority_levels"), nullable=False, default="Medium")
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())