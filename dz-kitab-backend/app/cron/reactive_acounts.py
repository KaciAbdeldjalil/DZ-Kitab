# app/cron/reactive_accounts.py

"""
Cron job pour réactiver automatiquement les comptes suspendus
À exécuter quotidiennement (par exemple à 2h du matin)

Configuration crontab:
0 2 * * * cd /app && python -m app.cron.reactive_accounts
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.rating_monitor import check_expired_suspensions
from datetime import datetime

def run_reactivation_job():
    """
    Tâche principale: vérifier et réactiver les comptes dont la suspension a expiré
    """
    print(f"\n{'='*60}")
    print(f"🕐 Démarrage du job de réactivation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    db: Session = SessionLocal()
    
    try:
        # Vérifier les suspensions expirées
        print("🔍 Vérification des suspensions expirées...")
        check_expired_suspensions(db)
        
        print(f"\n✅ Job terminé avec succès: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du job: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()
        print(f"{'='*60}\n")

if __name__ == "__main__":
    run_reactivation_job()
