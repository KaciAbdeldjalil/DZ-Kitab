import os
import sys
from pathlib import Path

# Fix: Ensure project root is in sys.path so 'app' can be imported
# In zero-config, the function is in /api/, so root is parent
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import traceback
    
    app = FastAPI()
    
    @app.get("/api/health")
    @app.get("/api")
    @app.get("/")
    async def startup_error(request=None):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Critical Startup Error (api/index.py v2.1.15)",
                "error": str(e),
                "trace": traceback.format_exc(),
                "cwd": os.getcwd(),
                "sys_path": sys.path
            }
        )
