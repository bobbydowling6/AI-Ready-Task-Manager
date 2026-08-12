import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from app.main import limiter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.schemas.users import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@limiter.limit("20/minute")
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(request: Request, credentials: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and return a token."""
    existing = db.query(User).filter(User.email == credentials.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=credentials.name,
        email=credentials.email,
        hashed_password=hash_password(credentials.password),
        is_active=True,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@limiter.limit("5/minute")
@router.post("/login", response_model=TokenResponse)
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """Log in and receive an access token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password.value):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@limiter.limit("60/minute")
@router.get("/me", response_model=UserResponse)
def read_current_user(request: Request, current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's information."""
    return current_user
