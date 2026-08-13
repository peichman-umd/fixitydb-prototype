import os
import sys

from dotenv import load_dotenv

from postgrest.fixity import FixityRecords

load_dotenv()
records = FixityRecords.from_config(os.environ)

try:
    number = int(sys.argv[1])
except IndexError:
    number = 250

for result in records.check_least_recent(number):
    records.record_result(result)
