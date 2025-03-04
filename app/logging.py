import os
import logging
import logging.config
import yaml
from app.config import LOGGING_CONFIG_PATH

def setup_logging(logging_config_path=LOGGING_CONFIG_PATH):
    os.makedirs(os.path.dirname(logging_config_path), exist_ok=True)
    
    with open(logging_config_path, 'r', encoding='utf-8') as f:
        logging_config = yaml.safe_load(f)
    
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.debug("Программа запущена успешно. Начало сбора логов")