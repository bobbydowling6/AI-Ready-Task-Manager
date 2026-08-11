from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

from sqlalchemy import Enum

class TaskCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete AI Project",
                "description": "Finish the AI project by the end of the week.",
                "due_date": "2024-06-30T23:59:59",
                "is_completed": False
            }
        }
    )

class GetTasks(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": [
                {
                    "id": 1,
                    "title": "Complete AI Project",
                    "description": "Finish the AI project by the end of the week.",
                    "due_date": "2024-06-30T23:59:59",
                    "is_completed": False,
                    "created_at": "2024-06-01T12:00:00"
                },
                {
                    "id": 2,
                    "title": "Prepare Presentation",
                    "description": "Prepare slides for the upcoming presentation.",
                    "due_date": None,
                    "is_completed": True,
                    "created_at": "2024-06-02T14:30:00"
                }
            ]
        }
    )

class GetSpecificTask(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)
    priority: str = Field(..., Enum("low", "medium", "high"))

class UpdateTask(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field(None, Enum("low", "medium", "high"))
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Task Title",
                "description": "Updated description for the task.",
                "priority": "medium",
                "due_date": "2024-07-15T12:00:00",
                "is_completed": True
            }
        }
    )    

class DeleteTask(BaseModel):
    id: int = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1
            }
        }
    )    

class CreateAiTask(BaseModel): 
    prompt: str = Field(..., max_length=1000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Generate a task for the AI project."
            }
        }
    )   