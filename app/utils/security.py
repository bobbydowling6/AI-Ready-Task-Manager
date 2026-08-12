from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db

SECRET_KEY = "dev-secret-key-change-me"  # [VERIFY] Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(http_bearer), db: Session = Depends(get_db)):
    """Dependency: validates the JWT and returns the current user."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # FIXED: Explicitly handle type extraction to satisfy strict type checkers
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Now safely cast or use user_id since it's verified not to be None
        str_user_id: str = str(user_id)
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    from app.models.users import User  # Import here to avoid circular imports
    user = db.query(User).filter(User.id == int(str_user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
