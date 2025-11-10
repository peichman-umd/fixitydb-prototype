from requests import Session
from requests_jwtauth import HTTPBearerAuth


class PostgrestService:
    def __init__(self, endpoint: str, auth_token: str = None):
        self.endpoint = endpoint
        self.session = Session()
        if auth_token is not None:
            self.session.auth = HTTPBearerAuth(auth_token)

    def get(self, path: str, **kwargs):
        return self.session.get(f'{self.endpoint}/{path}', **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(f'{self.endpoint}/{path}', **kwargs)
