import sys

from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT

secret = sys.argv[1]
role = sys.argv[2]

key = JWK.from_password(secret)
token = JWT(
    header={'alg': 'HS256', 'typ': 'JWT'},
    claims={'role': role},
)
token.make_signed_token(key)
print(token.serialize())
