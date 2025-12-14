from fastapi import APIRouter

# Cette ligne est CRITIQUE :
router = APIRouter()

@router.post("/register")
def register_user():
    return {"message": "Inscription utilisateur"}

@router.post("/login") 
def login_user():
    return {"message": "Connexion utilisateur"}

@router.get("/test")
def test_auth():
    return {"message": "Test réussi!"}


   