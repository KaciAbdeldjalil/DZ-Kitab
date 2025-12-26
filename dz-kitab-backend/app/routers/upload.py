# app/routers/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
import os
import uuid
from pathlib import Path
import shutil
from io import BytesIO
from PIL import Image

from app.middleware.auth import security

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads/books")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_IMAGE_FORMATS = {"jpeg", "png", "webp", "gif"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MIN_FILE_SIZE = 1024  # 1 KB
MAX_FILES_PER_UPLOAD = 5

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image using Pillow (Python 3.12+ safe)
    """

    # Extension check
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extension de fichier non autorisée"
        )

    # MIME type check
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type MIME non autorisé"
        )

    # File size check
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size < MIN_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop petit"
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop volumineux"
        )

    # Real image validation (content-based)
    try:
        image = Image.open(BytesIO(file.file.read()))
        image_format = image.format.lower()
        file.file.seek(0)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier n'est pas une image valide"
        )

    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d’image non supporté"
        )


def sanitize_filename(filename: str) -> str:
    import re
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


@router.post("/upload")
async def upload_book_image(
    file: UploadFile = File(...),
    token: str = Depends(security)
):
    validate_image_file(file)

    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Image uploadée avec succès",
        "filename": unique_filename,
        "url": f"/uploads/books/{unique_filename}",
        "size": os.path.getsize(file_path)
    }


@router.post("/upload-multiple")
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    token: str = Depends(security)
):
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES_PER_UPLOAD} fichiers autorisés"
        )

    uploaded, errors = [], []

    for file in files:
        try:
            validate_image_file(file)

            file_ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded.append({
                "original": file.filename,
                "filename": unique_filename,
                "url": f"/uploads/books/{unique_filename}"
            })

        except HTTPException as e:
            errors.append({"filename": file.filename, "error": e.detail})

    return {
        "uploaded": uploaded,
        "errors": errors,
        "total_uploaded": len(uploaded),
        "total_failed": len(errors)
    }


@router.delete("/delete/{filename}")
async def delete_image(
    filename: str,
    token: str = Depends(security)
):
    safe_filename = sanitize_filename(filename)
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image non trouvée")

    os.remove(file_path)

    return {
        "message": "Image supprimée avec succès",
        "filename": safe_filename
    }


@router.get("/test")
def test_upload():
    return {"message": "Upload router is working ✅"}
