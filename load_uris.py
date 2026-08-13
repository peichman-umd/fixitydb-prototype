import os
import sys

from dotenv import load_dotenv

from postgrest.fixity import FixityRecords

load_dotenv()
records = FixityRecords.from_config(os.environ)

filename = sys.argv[1]
with open(filename, mode='rb') as fh:
    records.bulk_add_uris(fh)
