from django.apps import AppConfig
from django.core.cache import cache


class MaiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crash'
    def ready(self):
        from . import signals
        
        
