import logging
from collections.abc import Iterable
from typing import Any

from requests import Session
from requests.auth import AuthBase

logger = logging.getLogger(__name__)


class PostgrestService:
    def __init__(self, endpoint: str, auth: AuthBase | None = None):
        self.endpoint = endpoint
        self.session = Session()
        self.session.auth = auth

    def get(self, path: str, **kwargs):
        return self.session.get(f'{self.endpoint}/{path}', **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(f'{self.endpoint}/{path}', **kwargs)

    def insert(self, path: str, record: dict[str, Any], upsert: bool = True):
        headers = {'Prefer': 'resolution=merge-duplicates'} if upsert else {}
        response = self.post(
            path=path,
            headers=headers,
            json=record,
        )
        if response.ok:
            logger.debug(f'Inserted {record} into {path}')
        else:
            raise PostgrestError(f'Unable to insert {record} into {path}: {response.text}')

        return response

    def bulk_insert(self, path: str, data: Iterable, media_type: str = 'text/csv', upsert: bool = True):
        headers = {'Content-Type': media_type}
        if upsert:
            headers['Prefer'] = 'resolution=merge-duplicates'
        response = self.post(
            path=path,
            headers=headers,
            data=data,
        )
        if response.ok:
            logger.info(f'Bulk insert to {path} succeeded')
        else:
            raise PostgrestError(f'Unable to bulk insert to {path}: {response.text}')


class PostgrestError(Exception):
    pass
