from django.apps import AppConfig


class MaiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crash'
    def ready(self):
        from . import signals
