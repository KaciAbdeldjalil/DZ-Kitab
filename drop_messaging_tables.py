import os
import sys
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import DATABASE_URL

print(f"Connecting to: {DATABASE_URL}")

drop_sql = """
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
"""

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Dropping messages and conversations tables...")
        conn.execute(text(drop_sql))
        conn.commit()
    print("Tables dropped successfully.")
except Exception as e:
    print(f"Error: {e}")
