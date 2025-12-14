from passlib.context import CryptContext
from datetime import timedelta
from .jwt import create_access_token

# Configuration bcrypt (nous le réinstallerons plus tard)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # Pour l'instant, utilisez SHA256 comme avant
    import hashlib
    hashed_input = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_input == hashed_password

def get_password_hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_token(user_id: int, email: str):
    # Créer un token JWT pour l'utilisateur
    access_token = create_access_token(
        data={"sub": email, "user_id": user_id}
    )
    return access_token