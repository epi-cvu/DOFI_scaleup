# tasks_des.py
"""
Tâches Celery - Lanceur de dés
"""
from celery import Celery
import time
import random
from celery_config_des import CELERY_CONFIG

# Crée l'instance Celery
celery = Celery('des')
celery.conf.update(CELERY_CONFIG)

@celery.task(bind=True)
def lancer_des(self, nombre_de_des):
    """
    Lance plusieurs dés (1-6)
    Affiche chaque résultat un par un
    """
    print(f"🎲 [WORKER] Lancement de {nombre_de_des} dés...")
    
    resultats = []
    
    for i in range(nombre_de_des):
        # Lance un dé (nombre entre 1 et 6)
        resultat = random.randint(1, 6)
        resultats.append(resultat)
        
        print(f"🎲 [WORKER] Dé {i+1}/{nombre_de_des} : {resultat}")
        
        # Calcule la progression
        progress = int((i + 1) / nombre_de_des * 100)
        
        # Met à jour l'état dans Redis
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': nombre_de_des,
                'progress': progress,
                'resultats': resultats.copy(),
                'dernier_de': resultat,
                'total_actuel': sum(resultats)
            }
        )
        
        # Suspense !
        time.sleep(0.5)
    
    # Statistiques finales
    total = sum(resultats)
    moyenne = total / len(resultats)
    
    print(f"✅ [WORKER] Terminé ! Total : {total}")
    
    return {
        'resultats': resultats,
        'total': total,
        'moyenne': round(moyenne, 2),
        'nombre_de_des': len(resultats),
        'min': min(resultats),
        'max': max(resultats)
    }

if __name__ == '__main__':
    print("="*60)
    print("Pour lancer le worker :")
    print("celery -A tasks_des worker --loglevel=info")
    print("="*60)