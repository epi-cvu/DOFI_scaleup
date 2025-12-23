# tasks_inv.py
"""
Tâches Celery - Inversion de texte
"""
from celery import Celery
import time
from celery_config_inv import CELERY_CONFIG

# Crée l'instance Celery
celery = Celery('inverseur')
celery.conf.update(CELERY_CONFIG)

# ============================================
# TÂCHE
# ============================================

@celery.task(bind=True)
def inverser_texte(self, texte):
    """
    Inverse un texte caractère par caractère
    Affiche la progression en temps réel
    """
    print(f"🔄 [WORKER] Inversion de : '{texte}'")
    
    resultat = ""
    total = len(texte)
    
    for i, char in enumerate(texte):
        # Ajoute le caractère au début (inversion)
        resultat = char + resultat
        
        # Calcule la progression
        progress = int((i + 1) / total * 100)
        
        print(f"🔤 [WORKER] Progression : {progress}% - '{resultat}'")
        
        # Met à jour l'état dans Redis
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total,
                'progress': progress,
                'resultat_partiel': resultat,  # ← Nouveau !
                'caractere_actuel': char
            }
        )
        
        # Attend un peu pour voir l'animation
        time.sleep(0.3)
    
    print(f"✅ [WORKER] Résultat final : '{resultat}'")
    
    return {
        'texte_original': texte,
        'texte_inverse': resultat,
        'longueur': len(texte)
    }


if __name__ == '__main__':
    print("="*60)
    print("Pour lancer le worker :")
    print("celery -A tasks_inv worker --loglevel=info")
    print("="*60)