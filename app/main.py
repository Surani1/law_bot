import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot_handlers import start, help_command, input_data, select_doc, generate_doc, process_input_and_select, button_callback

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    help_handler = CommandHandler('help', help_command)
    application.add_handler(help_handler)
    
    input_handler = CommandHandler('input_data', input_data)
    application.add_handler(input_handler)
    
    select_handler = CommandHandler('select_doc', select_doc)
    application.add_handler(select_handler)
    
    generate_handler = CommandHandler('generate_doc', generate_doc)
    application.add_handler(generate_handler)
    
    input_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, process_input_and_select)
    application.add_handler(input_message_handler)
    
    button_handler = CallbackQueryHandler(button_callback)
    application.add_handler(button_handler)
    
    application.run_polling()

if __name__ == '__main__':
    main()
