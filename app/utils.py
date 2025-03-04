from app.config import LANGUAGES_PATH, LOGGING_CONFIG_PATH, BASE_DIR
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import yaml
import os
import logging
import logging.config

def load_messages(language):
    languages = LANGUAGES_PATH
    with open(languages, 'r', encoding='utf-8') as file:
        messages = yaml.safe_load(file)
        return messages.get(language, messages.get('ru'))  # RU/EN as default

def create_inline_menu(language):
    messages = load_messages(language)
    
    keyboard = [
        [InlineKeyboardButton(messages['button_commands'], callback_data='commands')],
        [InlineKeyboardButton(messages['button_select_doc'], callback_data='select_doc')],
        [InlineKeyboardButton(messages['button_generate_doc'], callback_data='generate')]
    ]
    return InlineKeyboardMarkup(keyboard)

def setup_logging(logging_config_path=LOGGING_CONFIG_PATH):
    """Setup log directory."""
    
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    with open(logging_config_path, "r", encoding="utf-8") as f:
        logging_config = yaml.safe_load(f)

    log_filename = logging_config["handlers"]["timed_file"]["filename"]
    log_filepath = os.path.join(BASE_DIR, log_filename)

    if not os.path.exists(log_filepath):
        open(log_filepath, "w").close()

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.debug("Программа запущена успешно. Начало сбора логов")