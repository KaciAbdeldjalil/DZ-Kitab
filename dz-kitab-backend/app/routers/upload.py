from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
import os
import uuid
from pathlib import Path
import shutil
from app.middleware.auth import security

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads/books")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Créer le dossier uploads s'il n'existe pas
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_image(file: UploadFile) -> None:
    """Valider le fichier uploadé"""
    # Vérifier l'extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension non autorisée. Utilisez: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Vérifier le type MIME
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image"
        )

@router.post("/upload", response_model=dict)
async def upload_book_image(
    file: UploadFile = File(...),
    token: str = Depends(security)
):
    """
    Upload d'une image de livre (ROUTE PROTÉGÉE)
    
    - **file**: Fichier image (JPG, PNG, WEBP)
    - Maximum 5 MB
    - Retourne l'URL de l'image uploadée
    """
    try:
        # Valider le fichier
        validate_image(file)
        
        # Vérifier la taille du fichier
        file.file.seek(0, 2)  # Aller à la fin du fichier
        file_size = file.file.tell()  # Obtenir la position (= taille)
        file.file.seek(0)  # Revenir au début
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fichier trop volumineux. Maximum: {MAX_FILE_SIZE / (1024*1024)} MB"
            )
        
        # Générer un nom unique
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Retourner l'URL relative
        file_url = f"/uploads/books/{unique_filename}"
        
        return {
            "message": "Image uploadée avec succès",
            "filename": unique_filename,
            "url": file_url,
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )

@router.post("/upload-multiple", response_model=dict)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    token: str = Depends(security)
):
    """
    Upload multiple d'images (maximum 5 images)
    
    - **files**: Liste de fichiers images
    - Maximum 5 images par requête
    - Chaque image: maximum 5 MB
    """
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 images par upload"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Valider chaque fichier
            validate_image(file)
            
            # Vérifier la taille
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append({
                    "filename": file.filename,
                    "error": "Fichier trop volumineux"
                })
                continue
            
            # Générer nom unique et sauvegarder
            file_ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "original_filename": file.filename,
                "filename": unique_filename,
                "url": f"/uploads/books/{unique_filename}",
                "size": file_size
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "message": f"{len(uploaded_files)} image(s) uploadée(s)",
        "uploaded": uploaded_files,
        "errors": errors if errors else None
    }

@router.delete("/delete/{filename}")
async def delete_image(
    filename: str,
    token: str = Depends(security)
):
    """
    Supprimer une image (ROUTE PROTÉGÉE)
    
    - **filename**: Nom du fichier à supprimer
    """
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image non trouvée"
            )
        
        # Supprimer le fichier
        os.remove(file_path)
        
        return {
            "message": "Image supprimée avec succès",
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )