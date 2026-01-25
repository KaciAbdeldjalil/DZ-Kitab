import subprocess
import os

env_vars = {
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "JWT_SECRET_KEY": "2b87beba9e6551eee16f3ffd8b93f683",
    "ALLOWED_ORIGINS": "https://dz-kitab-frontend.vercel.app,https://dz-kitab-frontend-abdeldjalil-kacis-projects.vercel.app",
    "DATABASE_URL": "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
}

# Current directory should be fine if run from dz-kitab-backend
for key, value in env_vars.items():
    print(f"Cleaning and setting {key}...")
    subprocess.run(["vercel", "env", "rm", key, "production", "--yes"], capture_output=True)
    subprocess.run(["vercel", "env", "add", key, "production"], input=value, encoding="utf-8", capture_output=True)

print("Redeploying...")
subprocess.run(["vercel", "--prod", "--yes", "--force"], capture_output=True)
print("Done!")
