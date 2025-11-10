import os
import sys

from dotenv import load_dotenv

from postgrest.service import PostgrestService
from postgrest.fixity import FixityRecords

load_dotenv()
records = FixityRecords(
    endpoint=os.environ['FIXITYDB_ENDPOINT'],
    auth_token=os.environ['FIXITYDB_TOKEN'],
)

uri = sys.argv[1]
records.do_fixity_check(uri)
