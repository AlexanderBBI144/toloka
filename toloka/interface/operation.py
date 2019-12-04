import asyncio
from types import SimpleNamespace

from uuid import uuid4

from rest_api.requests import request
from toloka.interface.toloka import Toloka


# 61cd0956-caf4-4f32-aba1-b700b5022fba
class Operation(Toloka):
    endpoint = '/operations'
    types = SimpleNamespace(
        POOL = SimpleNamespace(
            OPEN = 'POOL.OPEN',
            CLOSE = 'POOL.CLOSE',
            ARCHIVE = 'POOL.ARCHIVE'
        ),
        PROJECT = SimpleNamespace(ARCHIVE='PROJECT.ARCHIVE'),
        TASK_SUITE = SimpleNamespace(BATCH_CREATE='TASK_SUITE.BATCH_CREATE'),
        TASK = SimpleNamespace(BATCH_CREATE='TASK.BATCH_CREATE'),
        PENDING = 'PENDING',
        RUNNING = 'RUNNING',
        SUCCESS = 'SUCCESS',
        FAIL = 'FAIL'
    )

    @classmethod
    async def list(cls, type=None, status=None, limit=None, sort='-submitted',
                              id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                              submitted_gt=None, submitted_gte=None,
                              submitted_lt=None, submitted_lte=None,
                              finished_gt=None, finished_gte=None,
                              finished_lt=None, finished_lte=None):
        return await super(Operation, cls).list(
            type=type, status=status, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            submitted_gt=submitted_gt, submitted_gte=submitted_gte,
            submitted_lt=submitted_lt, submitted_lte=submitted_lte,
            finished_gt=finished_gt, finished_gte=finished_gte,
            finished_lt=finished_lt, finished_lte=finished_lte
        )

    @classmethod
    async def get_operation(cls, id, log=False):
        url = f'{cls.host}/operations/{id}' if not log else f'{cls.host}/operations/{id}/log'
        return await request(cls.session, 'get', url=url)
