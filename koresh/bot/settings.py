import logging
import os
import sys
from datetime import timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from dotenv import load_dotenv


# TODO: refactor to have all the settings in a separate file
VERSION = '1.4.2'

load_dotenv()

BOT_API_TOKEN = os.environ['BOT_API_TOKEN']
TRANSLATOR_API_KEY = os.environ.get('TRANSLATOR_API_KEY')

PROXY_URL = 'socks5h://localhost:9050'
PROXIES = dict(
    http='socks5h://localhost:9050',
    https='socks5h://localhost:9050'
)
UPDATER_ARGS = {
    'proxy_url': PROXY_URL
}

BOT_CHAT_ID = os.environ['BOT_CHAT_ID']
ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']

# TODO: handle it's not set
BACKUP_MESSAGE_ID: Optional[int] = os.environ.get('BACKUP_MESSAGE_ID', None)

STORAGE_DIR = os.environ.get('STORAGE_DIR', f'{os.getcwd()}/.data_storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

CONFIRMATIONS_NEEDED = 2
COMMAND_RETRIES = 2
OLD_TRANSACTION_AGE = timedelta(hours=6)

# TODO: try more often
TRACKINGS_UPDATE_INTERVAL = timedelta(seconds=60)

TTL_IN_STATUS = timedelta(hours=2)

MAX_USER_PHOTOS = 13
SLADKO_EVERY_NTH_MESSAGE = 77
SAVE_LAST_MESSAGES_CNT = 10

LOGGING_LEVEL = logging.INFO
TELEGRAM_API_LOGGING_LEVEL = logging.INFO

LOGS_DIR = f'{os.getcwd()}/.logs'
os.makedirs(LOGS_DIR, exist_ok=True)
# 10000 here means infinity
rotating_file_handler = TimedRotatingFileHandler(f'{LOGS_DIR}/bot.log', backupCount=10000, when='D', interval=1)
console_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%I:%M:%S',
    level=LOGGING_LEVEL,
    **{'handlers': [console_handler, rotating_file_handler]}
)

logging.getLogger('telegram').setLevel(TELEGRAM_API_LOGGING_LEVEL)
logging.getLogger('JobQueue').setLevel(TELEGRAM_API_LOGGING_LEVEL)

logging.getLogger('telegram.ext.dispatcher').setLevel(LOGGING_LEVEL)
