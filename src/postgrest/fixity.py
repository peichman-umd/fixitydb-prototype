from collections.abc import Iterable
from email.utils import parsedate_to_datetime

import requests
from rdflib import Graph, URIRef, Namespace
from requests import Session
from requests_jwtauth import HTTPBearerAuth

premis = Namespace('http://www.loc.gov/premis/rdf/v1#')


class FixityRecords:
    def __init__(self, endpoint: str, auth_token: str = None):
        self.endpoint = endpoint
        self.session = Session()
        if auth_token is not None:
            self.session.auth = HTTPBearerAuth(auth_token)

    def add_uri(self, uri: str, last_modified: str):
        insert_res = self.session.post(
            url=f'{self.endpoint}/binaries',
            headers={
                # do an upsert operation
                'Prefer': 'resolution=merge-duplicates',
            },
            json={
                'uri': uri,
                'last_modified': last_modified,
            },
        )
        if insert_res.ok:
            print(f'Inserted {uri}')
        else:
            print(f'Unable to insert {uri}: {insert_res.text}')

    def bulk_add_uris(self, data: Iterable, media_type: str = 'text/csv'):
        bulk_res = self.session.post(
            url=f'{self.endpoint}/binaries',
            headers={
                'Content-Type': media_type,
                # do an upsert operation
                'Prefer': 'resolution=merge-duplicates',
            },
            data=data,
        )
        if bulk_res.ok:
            print(f'Inserted URIs')
        else:
            print(f'Unable to insert URIs: {bulk_res.text}')

    def get_least_recent(self, batch_size: int = 250):
        res = self.session.get(f'{self.endpoint}/least_recent', params={'limit': batch_size})
        return [row['uri'] for row in res.json()]

    def check_least_recent(self, batch_size: int = 250):
        for uri in self.get_least_recent(batch_size=batch_size):
            print(f'Checking {uri}')
            self.do_fixity_check(uri)

    def do_fixity_check(self, uri: str):
        fixity_check_uri = f'{uri}/fcr:fixity'

        fixity_res = requests.get(fixity_check_uri)
        mime_type = fixity_res.headers['Content-Type']
        if ';' in mime_type:
            mime_type = mime_type.split(';')[0]
        graph = Graph().parse(data=fixity_res.text, format=mime_type)
        check_uri = graph.value(URIRef(uri), premis.hasFixity)
        outcome = graph.value(check_uri, premis.hasEventOutcome)

        check_data = {
            "binary_uri": uri,
            "success": str(outcome) == 'SUCCESS',
            "time": str(parsedate_to_datetime(fixity_res.headers['Date'])),
            "result": graph.serialize(),
        }

        # print(check_data)

        insert_res = self.session.post(f'{self.endpoint}/checks', json=check_data)
        if insert_res.ok:
            print(f'Inserted {outcome} result for {uri}')
        else:
            print(f'Unable to insert {outcome} result for {uri}: {insert_res.text}')
