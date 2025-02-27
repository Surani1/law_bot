import logging
from fpdf import FPDF
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils import create_inline_menu
from bot.document_generator import load_templates

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = create_inline_menu()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для работы с документами. Выберите действие:", reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Доступные команды:\n"
                                                                     "/start - Начать работу с ботом\n"
                                                                     "/help - Показать эту справку\n"
                                                                     "/select_doc - Выбрать документ\n"
                                                                     "/input_data - Ввести данные для документа\n"
                                                                     "/generate_doc - Сгенерировать выбранный документ")


async def input_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'selected_doc' in context.user_data:
        required_fields = context.user_data['selected_doc']['fields']
        text = "Введите данные для документа через запятую:\n"
        for field in required_fields:
            text += f"- {field}\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Сначала выберите документ.")
    
    context.user_data['input_step'] = 'data'

async def process_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'input_step' in context.user_data and context.user_data['input_step'] == 'data':
        data = update.message.text
        
        # Разделение по запятой
        fields = [field.strip() for field in data.split(',')]
        
        # Проверьте количество полей
        if 'selected_doc' in context.user_data:
            required_fields = context.user_data['selected_doc']['fields']
            if len(fields) != len(required_fields):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Неправильный формат ввода. Ожидается {len(required_fields)} полей.")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, введите данные заново.")
                return
        
        # Сохраните данные в контексте
        context.user_data['fields'] = dict(zip(required_fields, fields))
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Данные приняты. Теперь вы можете сгенерировать документ.")

async def select_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    yaml_file_path = r'data\templates.yaml'
    templates = load_templates(yaml_file_path)
    
    if not templates:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет документов для выбора.")
        return
    
    text = "Выберите документ:\n"
    for i, doc in enumerate(templates):
        text += f"{i+1}. {doc['title']}\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    context.user_data['input_step'] = 'select_doc'
    context.user_data['templates'] = templates

async def process_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'input_step' in context.user_data and context.user_data['input_step'] == 'select_doc':
        try:
            doc_number = int(update.message.text)
            templates = context.user_data['templates']
            
            if doc_number < 1 or doc_number > len(templates):
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Неправильный номер документа.")
                return
            
            selected_doc = templates[doc_number - 1]
            context.user_data['selected_doc'] = selected_doc
            
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Документ выбран. Теперь вы можете ввести данные.")
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Неправильный формат ввода. Введите номер документа.")

async def generate_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        selected_doc = context.user_data.get('selected_doc')
        if not selected_doc:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Сначала выберите документ.")
            return
        
        user_data = context.user_data.get('fields')
        if not user_data:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Сначала введите данные для документа.")
            return
        
        # Генерируйте документ
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', r'data\DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        
        template = selected_doc['template_text']
        filled_template = template.format(**user_data)
        
        for line in filled_template.split('\n'):
            pdf.cell(200, 10, txt=line, ln=True, align='L')
        
        pdf.output('generated.pdf')
        
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open('generated.pdf', 'rb'))
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ошибка при генерации документа.")
        logging.error(f"Ошибка при генерации документа: {e}")

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
