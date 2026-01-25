import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

print(f"Applying additional schema fix to: {DATABASE_URL}")

fix_sql = """
-- 1. Add status column with default 'sent'
-- First create the type if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'messagestatus') THEN
        CREATE TYPE messagestatus AS ENUM ('sent', 'read', 'archived');
    END IF;
END $$;

ALTER TABLE messages ADD COLUMN IF NOT EXISTS status messagestatus DEFAULT 'sent';

-- 2. Add indices for better performance
CREATE INDEX IF NOT EXISTS ix_messages_status ON messages (status);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);
"""

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(fix_sql))
        conn.commit()
    print("Schema fix applied successfully!")
except Exception as e:
    print(f"Error applying fix: {e}")
