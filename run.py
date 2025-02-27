import sys
from bot.logging import setup_logging
sys.path.append('bot')

from bot.main import main

if __name__ == '__main__':
    logs = setup_logging()
    main()