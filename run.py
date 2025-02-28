import sys
from app.logging import setup_logging
sys.path.append('bot')

from app.main import main

if __name__ == '__main__':
    logs = setup_logging()
    main()