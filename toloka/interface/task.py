import asyncio
from dataclasses import dataclass, field, InitVar, make_dataclass
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace
from typing import Any, List, Dict

from pprint import pprint
import simplejson as json
from tqdm import tqdm
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface.toloka import Toloka
from toloka.interface.quality import Config
from toloka.utils import is_empty


@dataclass_json
@dataclass
class KnownSolution:
    output_values: 'OutputValues'
    correctness_weight: float = None

@dataclass_json
@dataclass
class TaskData:
    input_values: 'InputValues'
    id: str = None
    pool_id: str = None
    origin_task_id: str = None
    known_solutions: List[KnownSolution] = None
    message_on_unknown_solution: str = None
    overlap: int = None
    infinite_overlap: bool = None
    origin_task_id: str = None
    reserved_for: List[str] = None
    unavailable_for: List[str] = None
    created: str = None


class Task(Toloka):
    endpoint = '/tasks'
    data_class = TaskData
    max_limit = 100000

    def create(self, async_mode=None, allow_defaults=None, skip_invalid_items=None,
               open_pool=None, operation_id=None):
        return super(Task, self).create(params={
            'async_mode': str(async_mode).lower() if async_mode is not None else None,
            'allow_defaults': str(allow_defaults).lower() if allow_defaults is not None else None,
            'skip_invalid_items': str(skip_invalid_items).lower() if skip_invalid_items is not None else None,
            'open_pool': str(open_pool).lower() if open_pool is not None else None,
            'operation_id': str(operation_id) if operation_id is not None else None
        })

    @classmethod
    async def list(cls, pool_id=None, limit=max_limit, sort='id',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None,
                   overlap=None, overlap_gt=None, overlap_gte=None,
                   overlap_lt=None, overlap_lte=None):
        return await super(Task, cls).list(
            pool_id=pool_id, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            overlap=overlap, overlap_gt=overlap_gt, overlap_gte=overlap_gte,
            overlap_lt=overlap_lt, overlap_lte=overlap_lte
        )

    @classmethod
    async def list_all(cls, pool_id=None, created_gt=None, created_gte=None,
                       created_lt=None, created_lte=None, overlap=None,
                       overlap_gt=None, overlap_gte=None,
                       overlap_lt=None, overlap_lte=None):
        return await super(Task, cls).list_all(
            pool_id=pool_id, created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            overlap=overlap, overlap_gt=overlap_gt, overlap_gte=overlap_gte,
            overlap_lt=overlap_lt, overlap_lte=overlap_lte
        )

    @classmethod
    async def change_overlap(cls, pool_id, overlap, infinite_overlap):
        ids = [x['id'] for x in await cls.list_all(pool_id=pool_id) if x['overlap'] != overlap]
        for id in tqdm(ids):
            await cls.patch(
                id,
                data={
                    'overlap': overlap,
                    'infinite_overlap': infinite_overlap
                }
            )


async def create_tasks(pool_id, rows, cols, known_solutions_cols, annotation_col):
    input_values_cols = [x for x in cols if x not in known_solutions_cols + [annotation_col]]

    input_values = [[
            y for y, c in zip(x, cols)
            if c in input_values_cols
        ] for x in rows]
    known_solutions = [[[
            y for y, c in zip(x, cols)
            if c in known_solutions_cols and y is not None
        ]] for x in rows]
    message_on_unknown_solution = [
        y for x in rows for y, c in zip(x, cols)
        if c == annotation_col
    ]

    InputValues = make_dataclass('InputValues', input_values_cols)
    OutputValues = make_dataclass('OutputValues', known_solutions_cols)

    task = Task(data=[
        TaskData(
            input_values=InputValues(**dict(zip(input_values_cols, i))),
            known_solutions=[
                KnownSolution(
                    output_values=OutputValues(**dict(zip(known_solutions_cols, o)))
                ) for o in k
            ] if not is_empty(k) else None,
            message_on_unknown_solution=m,
            pool_id=pool_id,
            overlap=None,
            infinite_overlap=True if not is_empty(k) else None
        )
        for i, k, m in zip(
            input_values,
            known_solutions,
            message_on_unknown_solution
        )
    ])

    result = await task.create(async_mode=True, allow_defaults=True,
                               skip_invalid_items=False,
                               operation_id=str(uuid4()))
    print(f"Operation id: {result['result']['id']}")
    return result['result']['id']

    # result = await task.create(async_mode=False, allow_defaults=True)
    # pprint(result)
