# app/cron/reactive_accounts.py

"""
Cron job pour ractiver automatiquement les comptes suspendus
 excuter quotidiennement (par exemple  2h du matin)

Configuration crontab:
0 2 * * * cd /app && python -m app.cron.reactive_accounts
"""

import sys
import os
from pathlib import Path

# Ajouter le rpertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.rating_monitor import check_expired_suspensions
from datetime import datetime

def run_reactivation_job():
    """
    Tche principale: vrifier et ractiver les comptes dont la suspension a expir
    """
    print(f"\n{'='*60}")
    print(f" Dmarrage du job de ractivation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    db: Session = SessionLocal()
    
    try:
        # Vrifier les suspensions expires
        print(" Vrification des suspensions expires...")
        check_expired_suspensions(db)
        
        print(f"\n Job termin avec succs: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f" Erreur lors de l'excution du job: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()
        print(f"{'='*60}\n")

if __name__ == "__main__":
    run_reactivation_job()
