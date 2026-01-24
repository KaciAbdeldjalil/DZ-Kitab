ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
UPDATE users SET is_admin = FALSE WHERE is_admin IS NULL;
ALTER TABLE users ALTER COLUMN is_admin SET NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

INSERT INTO users (email, username, hashed_password, first_name, last_name, is_active, is_admin, created_at)
VALUES ('admin@dzkitab.com', 'admin_dzkit', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5I92rMq.x2uP6', 'Super', 'Admin', true, true, CURRENT_TIMESTAMP)
ON CONFLICT (email) DO UPDATE SET is_admin = true, is_active = true;

SELECT id, email, username, is_admin FROM users WHERE is_admin = true;
