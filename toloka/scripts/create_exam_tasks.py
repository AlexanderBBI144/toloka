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
from toloka.interface.task import Task, TaskData, create_tasks
from toloka.interface.operation import Operation

MODE = "main"
POOL_ID = "8823032"
DATE_END = "2019-11-01"

#53682
async def main():
    query = read_text(queries, 'create_exam_tasks.sql')
    res, cols = select(query, DATE_END)
    known_solutions_cols = ['result']
    input_values_cols = [x for x in cols if x not in known_solutions_cols + ['message_on_unknown_solution']]
    input_values = [[
            y for y, c in zip(x, cols)
            if c in input_values_cols
        ] for x in res]
    known_solutions = [[[
            y for y, c in zip(x, cols)
            if c in known_solutions_cols
        ]] for x in res]
    message_on_unknown_solution = [y for x in res for y, c in zip(x, cols)
                                   if c == 'message_on_unknown_solution']
    await create_tasks(
        pool_id=POOL_ID, mode=MODE, input_values=input_values, input_values_cols=input_values_cols,
        known_solutions=known_solutions, known_solutions_cols=known_solutions_cols,
        message_on_unknown_solution=message_on_unknown_solution
    )


if __name__ == '__main__':
    asyncio.run(main())
