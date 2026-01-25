import os
import sys
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import DATABASE_URL

print(f"Targeting DB: {DATABASE_URL}")

fix_sql = [
    "ALTER TABLE messages ADD COLUMN IF NOT EXISTS conversation_id INTEGER",
    "ALTER TABLE messages ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'sent'",
    "ALTER TABLE messages ADD COLUMN IF NOT EXISTS read_at TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE messages DROP COLUMN IF EXISTS announcement_id",
    # Conversations table fix (just in case)
    "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE"
]

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        for stmt in fix_sql:
            try:
                print(f"Executing: {stmt}")
                conn.execute(text(stmt))
                conn.commit()
            except Exception as se:
                print(f"Skip/Error: {se}")
        
        # Verify
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'messages'"))
        cols = [r[0] for r in result.fetchall()]
        print(f"VERIFIED_COLS:{','.join(cols)}")
        
except Exception as e:
    print(f"FATAL_ERROR:{e}")
