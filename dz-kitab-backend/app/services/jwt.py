# app/services/jwt.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "2b87beba9e6551eee16f3ffd8b93f683")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
# Default to 30 days (1 month) = 30 * 24 * 60 = 43200 minutes
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crer un token JWT"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Vrifier et dcoder un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f" JWT Error: {e}")
        return None
    except Exception as e:
        print(f" Token verification error: {e}")
        return None
