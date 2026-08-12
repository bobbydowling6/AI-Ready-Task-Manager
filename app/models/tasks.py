from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum  # Aliased to avoid naming conflict
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# 1. Define your Python Enum cleanly outside the model
class PriorityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Task(Base):
    __tablename__ = "tasks"

    id = Column[int](Integer, primary_key=True, index=True)
    title = Column[str](String(200), nullable=False)
    description = Column[str](String(2000), nullable=True)

    # 3. FIXED: Added native_enum=False so SQLite treats it safely as a VARCHAR/string 
    # during tests, preventing type-coercion crashes.
    priority = Column[str](
        SQLEnum(PriorityLevel, name="priority_levels", native_enum=False),
        nullable=False,
        default=PriorityLevel.MEDIUM,
    )

    due_date = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    user = relationship("User", back_populates="tasks")