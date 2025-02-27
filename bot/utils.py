from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_menu():
    keyboard = [
        [InlineKeyboardButton("Команды", callback_data='commands')],
        [InlineKeyboardButton("Выбрать документ", callback_data='select_doc')],
        [InlineKeyboardButton("Сгенерировать документ", callback_data='generate')]
    ]
    return InlineKeyboardMarkup(keyboard)
