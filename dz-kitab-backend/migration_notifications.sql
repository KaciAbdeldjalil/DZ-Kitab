-- migration_notifications.sql

-- 1. Créer l'enum pour les types de notifications
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notificationtype') THEN
        CREATE TYPE notificationtype AS ENUM (
            'new_rating',
            'rating_reply',
            'announcement_sold',
            'announcement_reserved',
            'low_rating_alert',
            'account_suspended',
            'account_reactivated',
            'message_received',
            'price_drop'
        );
    END IF;
END $$;

-- 2. Créer la table notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notificationtype NOT NULL,
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    related_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    related_announcement_id INTEGER REFERENCES announcements(id) ON DELETE SET NULL,
    related_rating_id INTEGER REFERENCES ratings(id) ON DELETE SET NULL,
    action_url VARCHAR,
    is_read BOOLEAN DEFAULT FALSE,
    is_sent_email BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

-- 3. Créer la table notification_preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_new_rating BOOLEAN DEFAULT TRUE,
    email_rating_reply BOOLEAN DEFAULT TRUE,
    email_announcement_sold BOOLEAN DEFAULT TRUE,
    email_low_rating_alert BOOLEAN DEFAULT TRUE,
    email_account_suspended BOOLEAN DEFAULT TRUE,
    email_message_received BOOLEAN DEFAULT TRUE,
    app_notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 4. Créer les index pour performance
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- 5. Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_notification_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Créer le trigger
DROP TRIGGER IF EXISTS update_notification_preferences_updated_at_trigger ON notification_preferences;
CREATE TRIGGER update_notification_preferences_updated_at_trigger
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_preferences_updated_at();

-- 7. Créer les préférences par défaut pour tous les utilisateurs existants
INSERT INTO notification_preferences (user_id)
SELECT id FROM users
WHERE id NOT IN (SELECT user_id FROM notification_preferences)
ON CONFLICT (user_id) DO NOTHING;

-- 8. Vérifier les tables créées
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('notifications', 'notification_preferences');

-- 9. Afficher la structure des tables
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('notifications', 'notification_preferences')
ORDER BY table_name, ordinal_position;

-- Message de confirmation
SELECT '✅ Migration notifications terminée avec succès!' as message;
