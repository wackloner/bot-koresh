import logging
from datetime import timedelta

API_TOKEN = '1221172107:AAG7GK7OBKMXLASZpbb4fME_SztgOoECF6o'

CONFIRMATIONS_NEEDED = 2
OLD_TRANSACTION_AGE = timedelta(hours=6)

POLLING_DELAY = timedelta(seconds=60)
TTL_IN_STATUS = timedelta(hours=2)


logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%I:%M:%S', level=logging.INFO)
