from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateSimple(BaseModel):
    """Schéma pour l'inscription"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schéma de réponse utilisateur"""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schéma de réponse pour le token JWT"""
    access_token: str
    token_type: str
    user: UserResponse