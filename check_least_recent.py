import os
import sys

from dotenv import load_dotenv

from postgrest.fixity import FixityRecords

load_dotenv()
records = FixityRecords(
    endpoint=os.environ['FIXITYDB_ENDPOINT'],
    auth_token=os.environ['FIXITYDB_TOKEN'],
)

try:
    number = int(sys.argv[1])
except IndexError:
    number = 250

records.check_least_recent(number)
