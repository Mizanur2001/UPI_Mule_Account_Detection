"""
JWT Authentication Module - Simplified Implementation
Handles user authentication with JWT tokens for secure API access.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "upi-mule-detection-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



# ── Pydantic Models ───────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str
    scopes: list = []


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


# ── Demo Users Database ───────────────────────────────────────────────────
DEMO_USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin@123"),
        "disabled": False,
    },
    "analyst": {
        "username": "analyst",
        "email": "analyst@example.com",
        "full_name": "Data Analyst",
        "hashed_password": pwd_context.hash("analyst@123"),
        "disabled": False,
    },
    "test": {
        "username": "test",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": pwd_context.hash("test@123"),
        "disabled": False,
    },
}


# ── Password Hashing ──────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Token Operations ──────────────────────────────────────────────────
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username, scopes=payload.get("scopes", []))
        return token_data
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


# ── User Authentication ───────────────────────────────────────────────────
def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password."""
    user_dict = DEMO_USERS_DB.get(username)
    if not user_dict:
        logger.warning(f"User {username} not found")
        return None
    if not verify_password(password, user_dict["hashed_password"]):
        logger.warning(f"Invalid password for user {username}")
        return None
    return User(**{k: v for k, v in user_dict.items() if k != "hashed_password"})


def create_user_tokens(user: User) -> Token:
    """Create access and refresh tokens for a user."""
    access_token = create_access_token(
        data={"sub": user.username, "scopes": []},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token)


# ── Dependency Functions ──────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency to get the current authenticated user from token.
    Used in protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
    return token_data


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Dependency to get the current active user.
    Ensures user is not disabled.
    """
    if current_user.username in DEMO_USERS_DB:
        user_dict = DEMO_USERS_DB[current_user.username]
        if user_dict.get("disabled", False):
            raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
