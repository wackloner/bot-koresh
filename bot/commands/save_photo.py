import logging
import os
from datetime import datetime
from typing import Optional

import requests

from bot.settings import PROXIES, API_TOKEN, STORAGE_DIR


def save_photo(file_id: str, photo_extra: Optional[str]) -> bool:
    logging.info(f"Got photo '{file_id}'")
    try:
        # TODO: refactor
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

        if photo_extra is None:
            photo_extra = ''
        photo_dir = STORAGE_DIR
        filename_suf = ''
        if photo_extra.startswith('/'):
            photo_dir += photo_extra
            os.makedirs(photo_dir, exist_ok=True)
        elif photo_extra:
            filename_suf = '-' + '_'.join(photo_extra.split())

        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'{photo_dir}/{now_str}{filename_suf}.jpg'

        with open(filename, 'wb') as output_file:
            output_file.write(response.content)
        logging.debug(f"File '{filename}' was saved on disk!")

        return True

    except Exception as e:
        logging.exception(e)
        return False
