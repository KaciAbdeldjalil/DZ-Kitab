import os
import sys

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import DATABASE_URL, engine
from sqlalchemy import inspect

print(f"APP_DATABASE_URL:{DATABASE_URL}")

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"TABLES:{','.join(tables)}")
    if 'messages' in tables:
        cols = [c['name'] for c in inspector.get_columns('messages')]
        print(f"MESSAGES_COLS:{','.join(cols)}")
except Exception as e:
    print(f"ERROR:{e}")
