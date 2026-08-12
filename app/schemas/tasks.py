from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

from app.models.tasks import PriorityLevel


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: PriorityLevel = PriorityLevel.MEDIUM
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = False

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "Complete AI Project",
                "description": "Finish the AI project by the end of the week.",
                "priority": "Medium",
                "due_date": "2026-06-30T23:59:59",
                "is_completed": False,
            }
        },
    )


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: PriorityLevel
    due_date: Optional[datetime] = None
    is_completed: bool
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Complete AI Project",
                "description": "Finish the AI project by the end of the week.",
                "priority": "Medium",
                "due_date": "2026-06-30T23:59:59",
                "is_completed": False,
                "user_id": 1,
                "created_at": "2026-08-12T13:21:16",
                "updated_at": "2026-08-12T13:21:16"
            }
        },
    )


class UpdateTask(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[PriorityLevel] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "title": "Updated Task Title",
                "description": "Updated description for the task.",
                "priority": "Medium",
                "due_date": "2026-07-15T12:00:00",
                "is_completed": True,
            }
        },
    )


class TaskPatch(UpdateTask):
    pass


class CreateAiTask(BaseModel):
    prompt: str = Field(..., max_length=1000)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "prompt": "Generate a task for the AI project.",
            }
        },
    )