import asyncio
from dataclasses import dataclass, field, InitVar, make_dataclass
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace
from typing import Any, List, Dict

import simplejson as json
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface import Toloka
from toloka.quality import Config


@dataclass_json
@dataclass
class KnownSolutions:
    output_values: 'OutputValues'
    correctness_weight: float = None

@dataclass_json
@dataclass
class TaskData:
    input_values: 'InputValues'
    id: str = None
    pool_id: str = None
    origin_task_id: str = None
    known_solutions: KnownSolutions = None
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
    async def list(cls, pool_id=None, limit=None, sort='-created',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None,
                   overlap=None, overlap_gt=None, overlap_gte=None,
                   overlap_lt=None, overlap_lte=None):
        return await super(Task, cls).list(
            status=status, project_id=project_id, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            overlap=None, overlap_gt=overlap_gt, overlap_gte=overlap_gte,
            overlap_lt=overlap_lt, overlap_lte=overlap_lte
        )
