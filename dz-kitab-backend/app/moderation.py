# moderation.py
# Fonction simple de modration de contenu

BANNED_WORDS = [
    "insulte1", "insulte2", "spam", "interdit"
]

def is_content_safe(text):
    """
    Vrifie si le texte contient des mots interdits
    Retourne True si le contenu est safe, False sinon
    """
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word in text_lower:
            return False
    return True
