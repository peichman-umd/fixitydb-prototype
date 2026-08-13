import logging
from collections.abc import Iterable, Iterator, Mapping

from plastron.files import BinaryResource
from plastron.models.fedora import FedoraBinary
from plastron.repo import Repository
from requests_jwtauth import HTTPBearerAuth

from postgrest.service import PostgrestService

logger = logging.getLogger(__name__)


class FixityRecords:
    def __init__(self, pgrst: PostgrestService, repo: Repository):
        self.pgrst = pgrst
        self.repo = repo

    @classmethod
    def from_config(cls, config: Mapping[str, str]):
        pgrst_endpoint = config['FIXITYDB_ENDPOINT']
        pgrst_auth_token = config['FIXITYDB_TOKEN']

        repo_endpoint = config['FCREPO_ENDPOINT']
        repo_auth_token = config['FCREPO_TOKEN']

        return cls(
            pgrst=PostgrestService(pgrst_endpoint, HTTPBearerAuth(pgrst_auth_token)),
            repo=Repository.from_url(repo_endpoint, auth=HTTPBearerAuth(repo_auth_token)),
        )

    def add_uri(self, uri: str):
        resource = self.repo.read(uri, BinaryResource)
        obj = resource.describe(FedoraBinary)
        self.pgrst.insert(
            path='binaries',
            record={
                'uri': uri,
                'last_modified': str(obj.last_modified),
                'size': int(str(obj.size)),
                'digest': str(obj.digest),
            },
        )

    def bulk_add_uris(self, data: Iterable, media_type: str = 'text/csv'):
        self.pgrst.bulk_insert(
            path='binaries',
            data=data,
            media_type=media_type,
        )

    def get_least_recent(self, batch_size: int = 250) -> Iterator[str]:
        res = self.pgrst.get(path='least_recent', params={'limit': batch_size})
        for row in res.json():
            yield row['uri']

    def check_least_recent(self, batch_size: int = 250) -> Iterator[dict[str, str | int]]:
        for uri in self.get_least_recent(batch_size=batch_size):
            yield self.check(uri)

    def check(self, uri: str) -> dict[str, str | int]:
        logger.info(f'Checking {uri}')
        resource = self.repo.read(uri, BinaryResource)
        obj = resource.describe(FedoraBinary)
        fixity_details = resource.check_fixity()
        logger.info(f'Fixity check outcome for {uri}: {fixity_details.outcome}')
        return {
            'binary_uri': str(uri),
            'outcome': str(fixity_details.outcome),
            'time': fixity_details.timestamp.isoformat(),
            'size': int(str(fixity_details.size)),
            'digest': str(fixity_details.digest),
            'last_modified': str(obj.last_modified),
            'expected_size': int(str(obj.size)),
            'expected_digest': str(obj.digest),
        }

    def record_result(self, result: dict[str, str | int]):
        logger.debug(f'Recording result: {result}')
        self.pgrst.insert(path='results', record=result)
