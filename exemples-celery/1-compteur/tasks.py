# tasks.py
"""
Tâches Celery - Indépendant de Flask
"""
from celery import Celery
import time
from celery_config import CELERY_CONFIG

# Crée l'instance Celery
celery = Celery('compteur')
celery.conf.update(CELERY_CONFIG)

# ============================================
# TÂCHES
# ============================================

@celery.task(bind=True)
def compter_lentement(self, jusqu_a):
    """
    Compte jusqu'à un nombre, lentement
    Cette fonction NE connait PAS Flask
    """
    print(f"🔨 [WORKER] Début comptage jusqu'à {jusqu_a}")
    
    for i in range(1, jusqu_a + 1):
        print(f"🔢 [WORKER] Compte : {i}")
        
        # Met à jour la progression dans Redis
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i,
                'total': jusqu_a
            }
        )
        
        # Attend 1 seconde
        time.sleep(1)
    
    print(f"✅ [WORKER] Comptage terminé !")
    return f"Fini de compter jusqu'à {jusqu_a} !"


# Pour tester la tâche directement
if __name__ == '__main__':
    print("="*60)
    print("Pour lancer le worker :")
    print("celery -A tasks worker --loglevel=info")
    print("="*60)