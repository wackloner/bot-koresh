import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import requests

from bot.context import app_context
from bot.settings import PROXIES, API_TOKEN, STORAGE_DIR


# TODO: store in user object
from model.user import FileInfo
from utils.str_utils import parse_time


def get_user_dir(user_name: Optional[str]) -> str:
    photo_dir = STORAGE_DIR
    if user_name:
        photo_dir += f'/{user_name}'
    os.makedirs(photo_dir, exist_ok=True)
    return photo_dir


# TODO: optimize with caching
def get_local_file_path(user_name: Optional[str] = None, extra_info: Optional[str] = None) -> str:
    if extra_info is None:
        extra_info = ''

    user_dir = get_user_dir(user_name)

    if extra_info.startswith('/'):
        user_dir += extra_info
        os.makedirs(user_dir, exist_ok=True)
    else:
        extra_info = extra_info.replace('/', '')

    filename_suf = '-' + '_'.join(extra_info.split()) if extra_info else ''

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f'{user_dir}/{now_str}{filename_suf}.jpg'


def get_ttl(photo_extra_info: str) -> Optional[timedelta]:
    if photo_extra_info is None:
        return None
    ttls = [parse_time(token) for token in photo_extra_info.split() if parse_time(token) is not None]
    return ttls[0] if len(ttls) > 0 else None


# TODO: param to save in common directory
# TODO: param to schedule destroying
def save_photo(file_id: str, user_id: Optional[int] = None, user_name: Optional[str] = None, extra_info: Optional[str] = None) -> bool:
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
        ttl = get_ttl(extra_info)
        # TODO: apply TTLs
        file_info = FileInfo(file_id, file_path, local_file_path, datetime.now(), ttl)
        user = app_context.user_manager.get_or_create(user_id, user_name, 1)
        user.stored_files.append(file_info)

        with open(local_file_path, 'wb') as output_file:
            output_file.write(response.content)
        logging.debug(f"File '{local_file_path}' was saved on disk!")

        return True

    except Exception as e:
        logging.exception(e)
        return False
