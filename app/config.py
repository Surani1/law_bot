import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGING_CONFIG_PATH = os.path.join(BASE_DIR, r'config\\logging.yaml')
TEMPLATES_PATH = os.path.join(BASE_DIR, r'config\\templates.yaml')
LANGUAGES_PATH = os.path.join(BASE_DIR, r'config\\languages.yaml')