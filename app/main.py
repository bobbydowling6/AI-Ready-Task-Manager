from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.utils.exceptions import AppException, BadRequestException, DuplicateException, NotFoundException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import initialize_db
from app.models import tasks, users  # Import so Base registers all models

# Create tables and apply lightweight schema updates for local development
initialize_db()

limiter = Limiter(key_func=get_remote_address)

# Define tag metadata for Swagger/ReDoc documentation
tags_metadata = [
    {
        "name": "Users",
        "description": "Operations related to user authentication, registration, and token management.",
    },
    {
        "name": "Tasks",
        "description": "Endpoints for creating, reading, updating, and deleting Task records.",
    }
]

# Initialize FastAPI instance with app-level metadata
app = FastAPI(
    title="Task Manager API",
    description="""
API for managing task records with authentication, Pydantic validation, and SQLAlchemy ORM. 

This API allows for creating, reading, updating, and deleting task records while ensuring secure access through authentication mechanisms.

## Security Features
* **CORS Middleware:** Restricted to trusted origins (`http://localhost:8501`, `http://localhost:3000`).
* **Rate Limiting:** Protects endpoints against abuse (e.g., root endpoint limited to 60/minute).
* **Custom Exception Handling:** Standardized error responses via custom application exceptions.

## Quick Start
1. Register an account at `POST /users/register` or log in at `POST /users/login`.
2. Copy the `access_token` from the response.
3. Click the **Authorize** button in the top right and paste your token.
4. Start exploring and managing task records!
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": True, "detail": "Rate limit exceeded"}
    )
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

from app.routers import users as user_router
from app.routers import tasks as task_router

app.include_router(user_router.router)
app.include_router(task_router.router)

@app.get("/")
@limiter.limit("60/minute")
def read_root(request: Request):
    return {"message": "Task Manager API is running"}

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail}
    )
@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail}
    )
  
@app.exception_handler(DuplicateException)
async def duplicate_handler(request: Request, exc: DuplicateException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail}
    )

@app.exception_handler(BadRequestException)
async def bad_request_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail}
    )
