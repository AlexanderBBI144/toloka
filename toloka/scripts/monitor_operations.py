import asyncio
from importlib.resources import read_text
from dataclasses import make_dataclass
from time import sleep

from pprint import pprint
from tqdm import tqdm
from uuid import uuid4

from rest_api.db import select, execute_select
import toloka.queries as queries
from toloka.interface import Toloka
from toloka.task import Task, TaskData
from toloka.operation import Operation


SUBMITTED_GT = "2019-11-27T13:00:00"
STATUS = "RUNNING"

async def monitor_one_operation(id):
    with tqdm(desc=id, total=100, leave=True) as pbar:
        progress = 0
        while progress < 100:
            operation = await Operation.get(id)
            current_progress = operation['progress']
            pbar.update(current_progress - progress)
            progress = current_progress
            await asyncio.sleep(3)

async def main():
    async with Toloka.init_session() as session:
        operations = await Operation.list_operations(submitted_gt=SUBMITTED_GT, status=STATUS)
        print('Current operations:')
        await asyncio.gather(*[monitor_one_operation(x['id']) for x in operations['items']])
        print('\nAll operations have completed.')

if __name__ == '__main__':
    asyncio.run(main())
