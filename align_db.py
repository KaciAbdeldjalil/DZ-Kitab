import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Jalil.com0@localhost:5432/dz_kitab")

print(f"Aligning database schema at: {DATABASE_URL}")

alignment_sql = """
-- 1. Create messagestatus enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'messagestatus') THEN
        CREATE TYPE messagestatus AS ENUM ('sent', 'read', 'archived');
    END IF;
END $$;

-- 2. Update messages table
-- Add conversation_id
ALTER TABLE messages ADD COLUMN IF NOT EXISTS conversation_id INTEGER;

-- Add status
ALTER TABLE messages ADD COLUMN IF NOT EXISTS status messagestatus DEFAULT 'sent';

-- Add read_at (consistent with model)
ALTER TABLE messages ADD COLUMN IF NOT EXISTS read_at TIMESTAMP WITH TIME ZONE;

-- 3. Add foreign key for conversation_id
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_messages_conversation') THEN
        ALTER TABLE messages ADD CONSTRAINT fk_messages_conversation 
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 4. Clean up old/inconsistent columns
-- Check if announcement_id exists in messages and remove it (it belongs to conversations now)
ALTER TABLE messages DROP COLUMN IF EXISTS announcement_id;

-- 5. Ensure indices
CREATE INDEX IF NOT EXISTS ix_messages_status ON messages (status);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);
"""

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(alignment_sql))
        conn.commit()
    print("Database schema alignment completed successfully!")
except Exception as e:
    print(f"Error aligning schema: {e}")
