import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# CFG
LOGGING_CONFIG_PATH = os.path.join(BASE_DIR, r'config\\logging.yaml')
TEMPLATES_PATH = os.path.join(BASE_DIR, r'config\\templates.yaml')
LANGUAGES_PATH = os.path.join(BASE_DIR, r'config\\languages.yaml')

# FONT
ARIAL_UNICODE = os.path.join(BASE_DIR, r'data\\ArialUni')
ARIAL_UNICODE_BOLD = os.path.join(BASE_DIR, r'data\\ArialUniBold.ttf')
ARIAL_UNICODE_BOLD_ITALIC = os.path.join(BASE_DIR, r'data\\ArialUniBoldItalic.ttf')
ARIAL_UNICODE_ITALIC = os.path.join(BASE_DIR, r'data\\ArialUniITalic.ttf')