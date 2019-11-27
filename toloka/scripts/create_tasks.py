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


DATE_START = '2019-09-12'
DATE_END = '2019-09-13'
CAMERA = None
CONF = 0.8
MIN_QUALITY = -1000
TOP_LIMIT = 15

#53682
async def main():
    query = read_text(queries, 'create_tasks.sql')
    res, cols = select(query, DATE_START, DATE_END, CAMERA, CONF, MIN_QUALITY, TOP_LIMIT)

    InputValues = make_dataclass('InputValues', cols)

    task = Task(data=[
        TaskData(
            input_values=InputValues(**dict(zip(cols, x))),
            pool_id=Toloka.pool_id
        )
        for x in res
    ])

    async with Toloka.init_session() as session:
        result = await task.create(async_mode=True, allow_defaults=True, skip_invalid_items=False, operation_id=str(uuid4()))
        print(f"Operation id: {result['result']['id']}")

if __name__ == '__main__':
    asyncio.run(main())
