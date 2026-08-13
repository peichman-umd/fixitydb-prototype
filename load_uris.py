import os
import sys

from dotenv import load_dotenv
from plastron.repo import Repository
from requests_jwtauth import HTTPBearerAuth

from postgrest.fixity import FixityRecords
from postgrest.service import PostgrestService

load_dotenv()

pgrst_endpoint = os.environ['FIXITYDB_ENDPOINT']
pgrst_auth_token = os.environ['FIXITYDB_TOKEN']

repo_endpoint = os.environ['FCREPO_ENDPOINT']
repo_auth_token = os.environ['FCREPO_TOKEN']

records = FixityRecords(
    pgrst=PostgrestService(pgrst_endpoint, HTTPBearerAuth(pgrst_auth_token)),
    repo=Repository.from_url(repo_endpoint, auth=HTTPBearerAuth(repo_auth_token)),
)


filename = sys.argv[1]
with open(filename, mode='rb') as fh:
    records.bulk_add_uris(fh)
