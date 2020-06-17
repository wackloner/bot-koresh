import logging
import os
from dataclasses import dataclass
from datetime import timedelta
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

# TODO: env
MY_CHAT_ID = 60972166


# TODO: config
@dataclass
class Settings:
    troll_mode: ClassVar[bool] = False


VERSION = '0.9.0'

CONFIRMATIONS_NEEDED = 2
COMMAND_RETRIES = 2
OLD_TRANSACTION_AGE = timedelta(hours=6)


# TODO: try faster
TRACKINGS_UPDATE_INTERVAL = timedelta(seconds=60)

TTL_IN_STATUS = timedelta(hours=2)

SLADKO_EVERY_NTH_MESSAGE = 35

LOGGING_LEVEL = logging.DEBUG
TELEGRAM_API_LOGGING_LEVEL = logging.INFO

UPDATER_ARGS = {
    'proxy_url': PROXY_URL
}

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%I:%M:%S',
    level=LOGGING_LEVEL
)

logging.getLogger('telegram').setLevel(TELEGRAM_API_LOGGING_LEVEL)
logging.getLogger('JobQueue').setLevel(TELEGRAM_API_LOGGING_LEVEL)

logging.getLogger('telegram.ext.dispatcher').setLevel(LOGGING_LEVEL)
