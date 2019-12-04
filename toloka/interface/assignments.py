import asyncio
from dataclasses import dataclass, field, InitVar
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace
from typing import Any, List, Dict

import pandas as pd
import simplejson as json
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface.toloka import Toloka
from toloka.interface.quality import Config
from toloka.interface.task import TaskData


@dataclass_json
@dataclass
class Values:
    output_values: field(init=False)
    output_values_input: InitVar[Dict[str, Any]]

    def __post_init__(self, output_values_input):
        self.output_values = SimpleNamespace(**output_values_input)


@dataclass_json
@dataclass
class AssignmentData:
    id: str
    task_suite_id: str
    pool_id: str
    user_id: str
    status: str
    reward: float
    tasks: List[TaskData]
    created: str
    first_declined_solution_attempt: List[Values] = None
    solutions: List[Values] = None
    mixed: bool = None
    automerged: bool = None
    submitted: str = None
    accepted: str = None
    rejected: str = None
    skipped: str = None
    expired: str = None


class Assignment(Toloka):
    endpoint = '/assignments'
    data_class = AssignmentData
    max_limit = 10000

    @classmethod
    async def list(cls, status=None, task_id=None, task_suite_id=None,
                   pool_id=None, user_id=None, limit=max_limit, sort='id',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None,
                   submitted_gt=None, submitted_gte=None,
                   submitted_lt=None, submitted_lte=None):
        return await super(Assignment, cls).list(
            status=status, task_id=task_id, task_suite_id=task_suite_id,
            pool_id=pool_id, user_id=user_id, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            submitted_gt=submitted_gt, submitted_gte=submitted_gte,
            submitted_lt=submitted_lt, submitted_lte=submitted_lte
        )

    @classmethod
    async def list_all(cls, status=None, task_id=None, task_suite_id=None,
                       pool_id=None, user_id=None,
                       created_gt=None, created_gte=None,
                       created_lt=None, created_lte=None,
                       submitted_gt=None, submitted_gte=None,
                       submitted_lt=None, submitted_lte=None):
        return await super(Assignment, cls).list_all(
            status=status, task_id=task_id, task_suite_id=task_suite_id,
            pool_id=pool_id, user_id=user_id,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            submitted_gt=submitted_gt, submitted_gte=submitted_gte,
            submitted_lt=submitted_lt, submitted_lte=submitted_lte
        )


async def get_results(pool_id, mode=None, status=None):
    async with Toloka.init_session(mode) as session:
        cols = ['Id', 'TaskSuiteId', 'PoolId', 'UserId', 'TaskId',
                'EventId1', 'EventId2', 'Result', 'Doubt', 'Error']
        rows = []
        result = await Assignment.list_all(status=status, pool_id=pool_id)
        for i in result:
            for input_values, answer in zip(i['tasks'], i['solutions']):
                rows.append((
                    i['id'],
                    i['task_suite_id'],
                    i['pool_id'],
                    i['user_id'],
                    input_values['id'],
                    int(input_values['input_values']['image_left'].split('.')[0]),
                    int(input_values['input_values']['image_right'].split('.')[0]),
                    answer['output_values']['result'],
                    answer['output_values']['doubt'],
                    answer['output_values']['error']
                ))
        return rows, cols


def get_results_xlsx(path):
    df = pd.read_excel(path)
    return df.to_records(index=False).tolist(), df.columns.tolist()


def calc_overlap(rows, cols):
    df = pd.DataFrame.from_records(rows, columns=cols)
    df['index'] = df[['EventId1', 'EventId2']].apply(lambda x: frozenset((x['EventId1'], x['EventId2'])), axis=1)
    return df['index'].value_counts().sort_values()
