from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)  # FIXED: Added EmailStr validation
    password: str = Field(..., max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "password": "SecurePassword123!"
            }
        }
    )

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=100)  # FIXED: Added EmailStr validation
    password: str = Field(..., max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice.johnson@example.com",
                "password": "SecurePassword123!"
            }
        }
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "is_active": True,
                "created_at": "2026-08-12T13:21:16"
            }
        }
    )