import os
from telegram import Update
from telegram.ext import ContextTypes
from utils import create_inline_menu, load_messages
from document_generator import load_templates, generate_pdf

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = 'ru'  # RU/EN as default
    context.user_data['language'] = language
    messages = load_messages(language)
    
    keyboard = create_inline_menu(language)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['start'], reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    messages = load_messages(language)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['help'])

async def input_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    messages = load_messages(language)
    
    if 'selected_doc' in context.user_data:
        required_fields = context.user_data['selected_doc']['fields']
        text = messages['input_data']
        for field in required_fields:
            text += f"- {field}\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_error'])
    
    context.user_data['input_step'] = 'data'

async def process_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    messages = load_messages(language)
    
    if 'input_step' in context.user_data and context.user_data['input_step'] == 'data':
        data = update.message.text
        
        # Разделение по запятой
        fields = [field.strip() for field in data.split(',')]
        
        # Проверьте количество полей
        if 'selected_doc' in context.user_data:
            required_fields = context.user_data['selected_doc']['fields']
            if len(fields) != len(required_fields):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_format_error'].format(count=len(required_fields)))
                await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_repeat'])
                return
        
        # Сохраните данные в контексте
        context.user_data['fields'] = dict(zip(required_fields, fields))
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['input_data_success'])

async def select_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    messages = load_messages(language)
    
    yaml_file_path = r'config\templates.yaml'
    templates = load_templates(yaml_file_path)
    
    if not templates:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_error'])
        return
    
    text = messages['select_doc']
    for i, doc in enumerate(templates):
        text += f"{i+1}. {doc['title']}\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    context.user_data['input_step'] = 'select_doc'
    context.user_data['templates'] = templates

async def process_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    messages = load_messages(language)
    
    if 'input_step' in context.user_data and context.user_data['input_step'] == 'select_doc':
        try:
            doc_number = int(update.message.text)
            templates = context.user_data['templates']
            
            if doc_number < 1 or doc_number > len(templates):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_number_error'])
                return
            
            selected_doc = templates[doc_number - 1]
            context.user_data['selected_doc'] = selected_doc
            
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_success'])
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['select_doc_number_error'])

async def generate_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'ru')
    messages = load_messages(language)
    
    try:
        selected_doc = context.user_data.get('selected_doc')
        if not selected_doc:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_error'])
            return
        
        user_data = context.user_data.get('fields')
        if not user_data:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_data_error'])
            return
        
        template = selected_doc['template_text']
        output_filename = 'generated.pdf'
        
        generate_pdf(template, user_data, output_filename)
        
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output_filename, 'rb'))
        
        try:
            os.remove(output_filename)
        except FileNotFoundError:
            print("Файл не найден для удаления.")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
        
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages['generate_doc_error_message'])
        print(f"Ошибка при генерации документа: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'commands':
        await help_command(update, context)
    elif query.data == 'select_doc':
        await select_doc(update, context)
    elif query.data == 'input_data':
        await input_data(update, context)
    elif query.data == 'generate':
        await generate_doc(update, context)

async def process_input_and_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'input_step' in context.user_data:
        if context.user_data['input_step'] == 'data':
            await process_input(update, context)
        elif context.user_data['input_step'] == 'select_doc':
            await process_select(update, context)
