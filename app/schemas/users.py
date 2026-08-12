from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class RegisterRequest(BaseModel):
    name: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)
    grade_level: int = Field(..., gt=0, le=12)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"