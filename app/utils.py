from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import yaml

def load_messages(language):
    with open(r'config/languages.yaml', 'r', encoding='utf-8') as file:
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
