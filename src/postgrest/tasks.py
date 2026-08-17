import json
import logging
import os

from celery import Celery, group, Task
from celery.utils.log import get_task_logger
from dotenv import load_dotenv

from postgrest.fixity import FixityRecords

logger = get_task_logger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

records = FixityRecords.from_config(os.environ)
app = Celery('fixity', broker=os.environ['CELERY_BROKER'], backend=os.environ['CELERY_BACKEND'])


class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """This means the fixity check did NOT run successfully (e.g., there was a network
        communication error). In this case, it will notify DPI and the developers."""
        logger.error(f'unable to run task {self.name}[{task_id}] (args: {args}, kwargs: {kwargs}): {exc}')
        logger.error('TODO: notify DPI and developers')


@app.task(base=BaseTask)
def check_least_recent(batch_size: int = 250):
    logger.debug(f'Checking least-recent fixity for {batch_size} records')
    group(check_and_record_fixity.s(uri) for uri in records.get_least_recent(batch_size))()


@app.task(base=BaseTask)
def check_and_record_fixity(uri: str):
    chain = check_fixity.s(uri) | record_result.s()
    chain()


@app.task(base=BaseTask)
def check_fixity(uri: str):
    logger.info(f'Checking {uri}')
    return records.check(uri)


@app.task(base=BaseTask)
def record_result(result: dict[str, str | int]):
    fixity_success = result['outcome'] == 'SUCCESS'
    logger.debug(json.dumps(result, indent=None))
    logger.info(f'Recording fixity check for {result["uri"]}: {result["outcome"]}')
    records.record_result(result)
    if not fixity_success:
        logger.warning(f'Fixity check FAILED for {result["uri"]}')
        logger.warning('TODO: notify DPI')
    return result
