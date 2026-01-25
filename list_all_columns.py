import os
import sys
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    for table in ['messages', 'conversations']:
        print(f"--- TABLE: {table} ---")
        result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
        for row in result.fetchall():
            print(f"COLUMN: {row[0]}")
