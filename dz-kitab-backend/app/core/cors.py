# app/core/cors.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from typing import List

def get_allowed_origins() -> List[str]:
    """
    Returns a list of allowed origins depending on environment
    """
    environment = os.getenv("ENVIRONMENT", "development")
    allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")

    base_origins = [
        "https://dz-kitab-frontend.vercel.app",
        "https://dz-kitab-frontend-abdeldjalil-kacis-projects.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ]

    if environment == "production":
        origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]
        for bo in base_origins:
            if bo not in origins:
                origins.append(bo)
        return origins
    else:
        # development
        return base_origins + [
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]


def configure_cors(app: FastAPI) -> None:
    """
    Add CORS middleware to the FastAPI app
    """
    allowed_origins = get_allowed_origins()
    environment = os.getenv("ENVIRONMENT", "development")

    cors_config = {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
        ],
        "expose_headers": [
            "Content-Length",
            "Content-Range",
            "X-Total-Count",
        ],
        "max_age": 600
    }

    if environment == "production":
        cors_config["expose_headers"].extend([
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ])

    app.add_middleware(CORSMiddleware, **cors_config)
    print(f"CORS configured for {environment} environment")
    print(f"Allowed origins: {allowed_origins}")
