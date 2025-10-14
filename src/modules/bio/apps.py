from django.apps import AppConfig
import sys

class BioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.modules.bio'
    label = 'bio'

    def ready(self):
        # Проверяем, выполняются ли миграции
        is_migrating = any('migrate' in arg for arg in sys.argv)
        
        # Загружаем модели только если не выполняются миграции
        if not is_migrating:
            from src.modules.bio.ml.model_loader import preload_models
            preload_models()