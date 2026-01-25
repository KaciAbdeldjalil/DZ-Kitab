# app/main.py

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import time
from pathlib import Path

from app.core.cors import configure_cors
from app.database import engine, Base
from app.core.errors import (
    dzkitab_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    operational_error_handler,
    jwt_error_handler,
    general_exception_handler,
    DZKitabException
)
from app.core.logging_config import setup_logging, RequestLoggingMiddleware
from app.routers import (
    upload, books, condition, ratings, notifications, auth,
    wishlist, admin, recommendations, dashboard, messages, curriculum
)
from sqlalchemy.exc import IntegrityError, OperationalError
from jose import JWTError

# ===============================
# CREATE FASTAPI APP
# ===============================
app = FastAPI(
    title="DZ-Kitab API",
    version="2.1.2",
    description="API pour la plateforme d'échange de livres universitaires avec système de recommandations par cursus",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===============================
# ADD MIDDLEWARES
# ===============================
app.add_middleware(RequestLoggingMiddleware)

# ===============================
# CONFIGURE CORS
# ===============================
configure_cors(app)

# ===============================
# GLOBAL OPTIONS HANDLER (preflight for Vercel)
# ===============================
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str, request: Request):
    """
    Handle preflight OPTIONS requests for serverless deployment
    """
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "https://dz-kitab-frontend.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# ===============================
# REGISTER EXCEPTION HANDLERS
# ===============================
app.add_exception_handler(DZKitabException, dzkitab_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ===============================
# STATIC FILES
# ===============================
Path("uploads/books").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ===============================
# INCLUDE ROUTERS
# ===============================
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/images", tags=["Images"])
app.include_router(books.router, prefix="/api/books", tags=["Books & Announcements"])
app.include_router(condition.router, prefix="/api/condition", tags=["Book Condition"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["Wishlist"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["User Dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["Curriculum"])

# ===============================
# ROOT ENDPOINTS
# ===============================
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur DZ-Kitab API!", "version": "2.1.2"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# ===============================
# STARTUP
# ===============================
setup_logging()
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except Exception as e:
    print(f"Warning: Database init error: {e}")
