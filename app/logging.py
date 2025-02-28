import os
import logging
import logging.config
import yaml

def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    with open('config/logging.yaml', 'r', encoding='utf-8') as f:
        logging_config = yaml.safe_load(f)
    
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.debug("Программа запущена успешно. Начало сбора логов")
