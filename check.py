import os
import sys

from dotenv import load_dotenv

from postgrest.fixity import FixityRecords

load_dotenv()
records = FixityRecords.from_config(os.environ)

uri = sys.argv[1]
records.record_result(records.check(uri))
