from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import engine, Base, get_db
from app.models.user import User
from app.schemas.user import UserCreateSimple, UserLogin, UserResponse, TokenResponse
from app.middleware.auth import security
from app.services.auth import create_user_token, verify_password, get_password_hash
from app.routers import upload

print("🚀 Démarrage de l'application...")
Base.metadata.create_all(bind=engine)
app = FastAPI(title="DZ-Kitab API", version="1.0.0")

# Créer le dossier uploads s'il n'existe pas
Path("uploads/books").mkdir(parents=True, exist_ok=True)

# Servir les fichiers statiques (images uploadées)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Inclure les routers
app.include_router(upload.router, prefix="/api/images", tags=["Images"])

# ============================================
# ROUTES PUBLIQUES (NON PROTÉGÉES)
# ============================================

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur DZ-Kitab API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/auth/register", response_model=dict)
def register(user_data: UserCreateSimple, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    try:
        print(f"📧 Tentative d'inscription: {user_data.email}")
        
        # Vérifier si l'utilisateur existe
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email ou nom d'utilisateur déjà utilisé"
            )
        
        # Hash du mot de passe
        hashed_password = get_password_hash(user_data.password)
        
        # Créer l'utilisateur
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Utilisateur créé: {user.id}")
        return {
            "message": "Utilisateur créé avec succès",
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erreur serveur: {str(e)}"
        )

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Connexion utilisateur - RETOURNE UN JWT TOKEN"""
    try:
        print(f"🔐 Tentative de connexion: {credentials.email}")
        
        # Chercher l'utilisateur
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier le mot de passe
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier si le compte est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        
        # Créer le token JWT
        access_token = create_user_token(user.id, user.email)
        
        print(f"✅ Connexion réussie: {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la connexion"
        )

# ============================================
# ROUTES PROTÉGÉES (NÉCESSITENT JWT)
# ============================================

@app.get("/auth/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Récupérer les informations de l'utilisateur connecté"""
    try:
        # Obtenir l'email depuis le token
        from app.services.jwt import verify_token
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        )

@app.get("/books/")
def get_books(token: str = Depends(security)):
    """Liste des livres - ROUTE PROTÉGÉE"""
    return {
        "message": "Liste des livres disponibles",
        "books": []
    }

@app.get("/profile")
def get_profile(token: str = Depends(security), db: Session = Depends(get_db)):
    """Profil utilisateur - ROUTE PROTÉGÉE"""
    from app.services.jwt import verify_token
    payload = verify_token(token)
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    
    return {
        "message": "Profil utilisateur",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
    }

print("✅ Application prête! Accédez à: http://localhost:8000/docs")