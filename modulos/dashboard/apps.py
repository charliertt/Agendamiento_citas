from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modulos.dashboard'
    label = 'dashboard' 

def ready(self):
        import modulos.dashboard.signals