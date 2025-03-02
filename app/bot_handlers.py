import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.utils import create_inline_menu, load_messages
from app.document_generator import load_templates, generate_pdf_from_template

def get_language_and_messages(context):
    language = context.user_data.get('language', 'ru')
    return language, load_messages(language)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language, messages = get_language_and_messages(context)
    context.user_data['language'] = language
    keyboard = create_inline_menu(language)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['start'], reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language, messages = get_language_and_messages(context)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['help'])

async def input_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_language_and_messages(context)

    if 'selected_doc' in context.user_data:
        required_fields = context.user_data['selected_doc']['fields']
        text = messages['input_data'] + "\n".join([f"- {field}" for field in required_fields])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_error'])

    context.user_data['input_step'] = 'data'

async def process_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_language_and_messages(context)

    if 'input_step' in context.user_data and context.user_data['input_step'] == 'data':
        data = update.message.text
        fields = [field.strip() for field in data.split(',')]

        if 'selected_doc' in context.user_data:
            required_fields = context.user_data['selected_doc']['fields']
            if len(fields) != len(required_fields):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_format_error'].format(count=len(required_fields)))
                await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_repeat'])
                return

        context.user_data['fields'] = dict(zip(required_fields, fields))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_success'])

async def select_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_language_and_messages(context)

    yaml_file_path = r'config\templates.yaml'
    templates = load_templates(yaml_file_path)

    if not templates:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_error'])
        return

    text = messages['select_doc'] + "\n".join([f"{i+1}. {doc['title']}" for i, doc in enumerate(templates)])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    context.user_data['input_step'] = 'select_doc'
    context.user_data['templates'] = templates

async def process_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_language_and_messages(context)

    if 'input_step' in context.user_data and context.user_data['input_step'] == 'select_doc':
        try:
            doc_number = int(update.message.text)
            templates = context.user_data['templates']

            if not (1 <= doc_number <= len(templates)):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_number_error'])
                return

            selected_doc = templates[doc_number - 1]
            context.user_data['selected_doc'] = selected_doc

            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_success'])
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_number_error'])

async def generate_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language, messages = get_language_and_messages(context)
    
    try:
        selected_doc = context.user_data.get('selected_doc')
        user_data = context.user_data.get('fields')

        if not selected_doc or not user_data:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_error'])
            return

        output_filename = os.path.abspath('generated.pdf')

        if not generate_pdf_from_template(selected_doc, user_data, output_filename):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_error_message'])
            return

        try:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output_filename, 'rb'))
        except FileNotFoundError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_error_message'])
            logging.error(f"Файл {output_filename} не найден для отправки.")
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['file_not_found'])
            logging.error(f"Ошибка при отправке файла: {e}")

        os.remove(output_filename)  # Cleanup
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_error_full'])
        logging.error(f"Общая ошибка при генерации документа: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    command_map = {
        'commands': help_command,
        'select_doc': select_doc,
        'input_data': input_data,
        'generate': generate_doc
    }

    if query.data in command_map:
        await command_map[query.data](update, context)

async def process_input_and_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_step = context.user_data.get('input_step')
    if input_step == 'data':
        await process_input(update, context)
    elif input_step == 'select_doc':
        await process_select(update, context)
