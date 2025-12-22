# tasks_temp.py
"""
Tâches Celery - Conversion de température
"""
from celery import Celery
import time
from celery_config_temp import CELERY_CONFIG

# Crée l'instance Celery
celery = Celery('temperature')
celery.conf.update(CELERY_CONFIG)

# ============================================
# TÂCHE
# ============================================

@celery.task
def convertir_temperature(celsius):
    """
    Convertit Celsius en Fahrenheit
    Simule un calcul complexe avec un délai
    """
    print(f"🌡️  [WORKER] Conversion de {celsius}°C...")
    
    # Simule un calcul complexe (API externe, calcul lourd, etc.)
    time.sleep(3)
    
    # Formule de conversion
    fahrenheit = (celsius * 9/5) + 32
    
    # Calcule aussi Kelvin (bonus)
    kelvin = celsius + 273.15
    
    print(f"✅ [WORKER] Résultat : {fahrenheit}°F / {kelvin}K")
    
    return {
        'celsius': celsius,
        'fahrenheit': round(fahrenheit, 2),
        'kelvin': round(kelvin, 2),
        'message': f'{celsius}°C = {round(fahrenheit, 2)}°F = {round(kelvin, 2)}K'
    }


if __name__ == '__main__':
    print("="*60)
    print("Pour lancer le worker :")
    print("celery -A tasks_temp worker --loglevel=info")
    print("="*60)