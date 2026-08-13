import logging
import os

import click
from dotenv import load_dotenv

from postgrest.fixity import FixityRecords

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@click.command()
@click.option('--least-recent', is_flag=True)
@click.option('-n', '--number', type=int, default=250)
@click.argument('uri', required=False)
def check(uri, least_recent, number):
    records = FixityRecords.from_config(os.environ)
    if least_recent:
        for result in records.check_least_recent(number):
            records.record_result(result)
    elif uri:
        records.record_result(records.check(uri))
    else:
        pass
