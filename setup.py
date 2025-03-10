from setuptools import setup, find_packages

setup(
    name='telegram_bot_law',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot>=13.0',
        'PyYAML',
        'fpdf',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'run_bot = run:run',
        ],
    },
)