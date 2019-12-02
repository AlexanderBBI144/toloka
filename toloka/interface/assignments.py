import asyncio
from dataclasses import dataclass, field, InitVar
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace
from typing import Any, List, Dict

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

    @classmethod
    async def list(cls, status=None, task_id=None, task_suite_id=None,
                   pool_id=None, user_id=None, limit=None, sort=None,
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
