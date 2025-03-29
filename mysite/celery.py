import os
from celery import Celery

# Debe apuntar a TU MÓDULO settings.py real
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Usa el nombre de TU MÓDULO
app = Celery('mysite')  # ← ¡Cambiado a 'mysite'!
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()