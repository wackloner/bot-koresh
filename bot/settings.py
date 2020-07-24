import logging
import os
import sys
from dataclasses import dataclass
from datetime import timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import Optional, ClassVar

from dotenv import load_dotenv


load_dotenv()


API_TOKEN = os.environ['API_TOKEN']
PROXY_URL = 'socks5h://localhost:9050'

PROXIES = dict(
    http='socks5h://localhost:9050',
    https='socks5h://localhost:9050'
)

ADMIN_CHAT_ID: Optional[int] = os.environ.get('ADMIN_CHAT_ID', None)
DATA_STORAGE_MESSAGE_ID: Optional[int] = os.environ.get('DATA_STORAGE_MESSAGE_ID', None)

STORAGE_DIR = os.environ.get('STORAGE_DIR', f'{os.getcwd()}/.data_storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

# TODO: env
MY_CHAT_ID = 60972166


VERSION = '0.9.0'

CONFIRMATIONS_NEEDED = 2
COMMAND_RETRIES = 2
OLD_TRANSACTION_AGE = timedelta(hours=6)


# TODO: try faster
TRACKINGS_UPDATE_INTERVAL = timedelta(seconds=60)

TTL_IN_STATUS = timedelta(hours=2)

MAX_USER_PHOTOS = 13

SLADKO_EVERY_NTH_MESSAGE = 50

SAVE_LAST_MESSAGES_CNT = 10

LOGGING_LEVEL = logging.DEBUG
TELEGRAM_API_LOGGING_LEVEL = logging.INFO

UPDATER_ARGS = {
    'proxy_url': PROXY_URL
}


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
