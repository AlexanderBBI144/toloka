import asyncio
from importlib.resources import read_text
from dataclasses import make_dataclass
from time import sleep

from pprint import pprint
from tqdm import tqdm
from uuid import uuid4

from rest_api.db import select, execute_select
import toloka.queries as queries
from toloka.interface.toloka import Toloka
from toloka.interface.task import Task, TaskData
from toloka.interface.operation import Operation


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
    
if __name__ == '__main__':
    asyncio.run(main())
