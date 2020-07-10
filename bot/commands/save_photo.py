import logging
import os
from datetime import datetime
from typing import Optional

import requests

from bot.settings import PROXIES, API_TOKEN, STORAGE_DIR


def get_local_file_path(user_name: Optional[str] = None, extra_info: Optional[str] = None) -> str:
    if extra_info is None:
        extra_info = ''
    photo_dir = STORAGE_DIR
    if user_name:
        photo_dir += f'/{user_name}'

    filename_suf = ''
    if extra_info.startswith('/'):
        photo_dir += extra_info
    elif extra_info:
        filename_suf = '-' + '_'.join(extra_info.split())

    os.makedirs(photo_dir, exist_ok=True)

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f'{photo_dir}/{now_str}{filename_suf}.jpg'


# TODO: param to save in common directory
# TODO: param to schedule destroying
def save_photo(file_id: str, user_name: Optional[str] = None, extra_info: Optional[str] = None) -> bool:
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

        local_file_path = get_local_file_path(user_name, extra_info)

        with open(local_file_path, 'wb') as output_file:
            output_file.write(response.content)
        logging.debug(f"File '{local_file_path}' was saved on disk!")

        return True

    except Exception as e:
        logging.exception(e)
        return False
