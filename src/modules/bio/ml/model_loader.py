import os
from huggingface_hub import hf_hub_download
import joblib
from functools import lru_cache
import logging
from src.config.env import env
import threading

# Настройка логгера
logger = logging.getLogger(__name__)

# Настройки для Hugging Face Hub
DEFAULT_ORGANIZATION = 'ffillmore'
# Теперь обе модели хранятся в одном репозитории
MODEL_REPO = f"{DEFAULT_ORGANIZATION}/bio-classification-models"

# Имена файлов моделей
MODEL_FILENAMES = {
    'meadow': 'model_meadow.pkl',
    'forest': 'model_forest.pkl'
}

# Локальная директория для кеширования моделей
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cached_models')
os.makedirs(CACHE_DIR, exist_ok=True)

@lru_cache(maxsize=4)
def get_model(zone_type):
    """
    Загружает модель с Hugging Face Hub или из локального кэша.
    
    Args:
        zone_type (str): Тип местности ('meadow' или 'forest')
        
    Returns:
        model: Загруженная модель scikit-learn
        
    Raises:
        ValueError: Если указан неподдерживаемый тип местности
        Exception: При возникновении ошибок загрузки
    """
    if zone_type not in MODEL_FILENAMES:
        raise ValueError(f"Неподдерживаемый тип местности: {zone_type}. Поддерживаемые типы: {list(MODEL_FILENAMES.keys())}")
    
    filename = MODEL_FILENAMES[zone_type]
    local_cache_path = os.path.join(CACHE_DIR, filename)
    
    try:
        # Сначала пытаемся загрузить из кэша
        if os.path.exists(local_cache_path):
            logger.info(f"Загрузка модели {zone_type} из локального кэша")
            return joblib.load(local_cache_path)
        
        # Если в кэше нет, скачиваем с Hugging Face Hub
        logger.info(f"Скачивание модели {zone_type} с Hugging Face Hub")
        download_path = hf_hub_download(repo_id=MODEL_REPO, filename=filename, token=env.str('HF_TOKEN_READ', default=None))
        
        # Загружаем модель
        model = joblib.load(download_path)
        
        # Сохраняем в кэш для будущего использования
        logger.info(f"Сохранение модели {zone_type} в локальный кэш")
        joblib.dump(model, local_cache_path)
        
        return model
    
    except Exception as e:
        # Если есть резервная копия локально, пробуем загрузить её
        fallback_path = os.path.join('src', 'modules', 'bio', 'data', filename)
        if os.path.exists(fallback_path):
            logger.warning(f"Ошибка загрузки с Hugging Face Hub: {str(e)}. Используем резервную копию.")
            return joblib.load(fallback_path)
        else:
            logger.error(f"Не удалось загрузить модель {zone_type}: {str(e)}. Резервная копия не найдена.")
            raise Exception(f"Ошибка загрузки модели {zone_type}: {str(e)}. Резервная копия не найдена по пути {fallback_path}")

def preload_models():
    """
    Предварительно загружает все модели в кеш.
    Запускается в отдельном потоке, чтобы не блокировать запуск сервера.
    Загрузка выполняется только если файлы моделей отсутствуют в кеше.
    """
    # Проверяем, существуют ли все модели в кеше
    all_models_cached = True
    for zone_type in MODEL_FILENAMES:
        filename = MODEL_FILENAMES[zone_type]
        local_cache_path = os.path.join(CACHE_DIR, filename)
        if not os.path.exists(local_cache_path):
            all_models_cached = False
            break
    
    # Если все модели уже в кеше, не запускаем загрузку
    if all_models_cached:
        return None
    
    def _preload():
        for zone_type in MODEL_FILENAMES:
            filename = MODEL_FILENAMES[zone_type]
            local_cache_path = os.path.join(CACHE_DIR, filename)
            if os.path.exists(local_cache_path):
                continue
                
            try:
                get_model(zone_type)
                logger.info(f"Модель {zone_type} успешно предзагружена в кеш")
            except Exception as e:
                logger.error(f"Не удалось предзагрузить модель {zone_type}: {str(e)}")
    
    # Запускаем загрузку в отдельном потоке
    thread = threading.Thread(target=_preload, daemon=True)
    thread.start()
    return thread

def clear_cache():
    """Очищает кэш загруженных моделей"""
    get_model.cache_clear()
    logger.info("Кэш моделей очищен") 