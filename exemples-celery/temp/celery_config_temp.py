# celery_config_temp.py
"""
Configuration pour le convertisseur de température
"""

# Redis
BROKER_URL = 'redis://localhost:6379/0'
RESULT_BACKEND = 'redis://localhost:6379/0'

# Celery config
CELERY_CONFIG = {
    'broker_url': BROKER_URL,
    'result_backend': RESULT_BACKEND,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'Europe/Paris',
    'enable_utc': True,
}