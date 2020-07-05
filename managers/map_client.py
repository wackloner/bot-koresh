import logging
from dataclasses import dataclass
from typing import ClassVar, Any, Optional

import requests


@dataclass
class MapClient:
    STATIC_API_URL: ClassVar[str] = 'https://static-maps.yandex.ru/1.x/'

    IMAGE_SIZE = 300
    LANG_SYMBOL = 'ru_RU'
    MAP_TYPE = 'map'
    ZOOM = 5
    VIEWPORT_SIZE = 0.015

    def get_map_by_coordinates(self, coordinates: str) -> Optional[Any]:
        response = requests.get(self.STATIC_API_URL, params={
            'size': f'{self.IMAGE_SIZE},{self.IMAGE_SIZE}',
            'lang': self.LANG_SYMBOL,
            'l': self.MAP_TYPE,
            'z': self.ZOOM,
            'll': coordinates,
            'spn': f'{self.VIEWPORT_SIZE},{self.VIEWPORT_SIZE}'
        })

        logging.debug(f'\n----->{response.status_code}')
        logging.debug(f'\n----->{response.headers}')

        return response.content

    def get_img_link_by_coordinates(self, coordinates: str, spn_mul: float = 1) -> str:
        params = {
            'size': f'{self.IMAGE_SIZE},{self.IMAGE_SIZE}',
            'lang': self.LANG_SYMBOL,
            'l': self.MAP_TYPE,
            'z': self.ZOOM,
            'll': coordinates,
            'spn': f'{self.VIEWPORT_SIZE * spn_mul},{self.VIEWPORT_SIZE * spn_mul}',
            'pt': f'{coordinates},flag',
        }
        params_str = '&'.join(f'{k}={v}' for k, v in params.items())

        res = f'{self.STATIC_API_URL}?{params_str}'
        logging.debug(f'\n-----> {res}')

        return res
