from fastapi import APIRouter

# Cette ligne est CRITIQUE :
router = APIRouter()

@router.get("/")
def list_books():
    return {"message": "Liste des livres"}