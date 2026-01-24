-- 1. Ajouter is_admin si manquant
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- 2. Créer un index pour performance
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- 3. Créer un utilisateur admin par défaut
INSERT INTO users (
    email,
    username,
    hashed_password,
    first_name,
    last_name,
    is_active,
    is_admin,
    created_at
) VALUES (
    'admin@dzkitab.com',
    'admin_dzkit',
    -- Password: Admin123!@# (hashed with bcrypt)
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5I92rMq.x2uP6',
    'Super',
    'Admin',
    true,
    true,
    CURRENT_TIMESTAMP
) ON CONFLICT (email) DO UPDATE 
SET 
    is_admin = true,
    is_active = true;

-- 4. Vérifier
SELECT 
    id, 
    email, 
    username, 
    first_name, 
    last_name, 
    is_admin, 
    is_active 
FROM users 
WHERE is_admin = true;
