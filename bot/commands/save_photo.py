import logging
from datetime import datetime

import requests

from bot.settings import PROXIES, API_TOKEN


def save_photo(file_id: str) -> bool:
    logging.info(f"Got photo '{file_id}'")
    try:
        # TODO: refactor repeated code
        logging.debug(f'GET -> https://api.telegram.org/bot{API_TOKEN}/getFile?file_id={file_id}')
        response = requests.get(f'https://api.telegram.org/bot{API_TOKEN}/getFile?file_id={file_id}', proxies=PROXIES)

        if response.status_code != 200:
            logging.error(f'~~~ {response.status_code}\n{response.headers}')
            return False

        file_info = response.json()['result']
        logging.debug(file_info)

        file_path = file_info['file_path']

        logging.debug(f'GET -> https://api.telegram.org/file/bot{API_TOKEN}/{file_path}')
        response = requests.get(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}', proxies=PROXIES)
        if response.status_code != 200:
            logging.error(f'~~~ {response.status_code}\n{response.headers}')
            return False

        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f'.photo_storage/{now_str}.jpg', 'wb') as output_file:
            output_file.write(response.content)
        return True

    except Exception as e:
        logging.exception(e)
        return False
