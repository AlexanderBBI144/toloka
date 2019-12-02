import asyncio
from dataclasses import dataclass, field, InitVar
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace

import simplejson as json
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface.toloka import Toloka


@dataclass_json
@dataclass
class SkillData:
    name: str
    id: str = None
    private_comment: str = None
    hidden: bool = None
    training: bool = None
    skill_ttl_hours: int = None
    created: str = None


class Skill(Toloka):
    endpoint = '/skills'
    data_class = SkillData

    @classmethod
    async def list(cls, name=None, limit=None, sort='-created',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None):
        return await super(Skill, cls).list(
            name=name, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte
        )


@dataclass_json
@dataclass
class UserSkillData:
    skill_id: str
    user_id: str
    value: int
    id: str = None
    exact_value: float = None
    created: str = None


class UserSkill(Toloka):
    endpoint = '/user-skills'
    data_class = UserSkillData

    @classmethod
    async def list(cls, skill_id=None, user_id=None, limit=None, sort='-created',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None,
                   modified_gt=None, modified_gte=None,
                   modified_lt=None, modified_lte=None):
        return await super(UserSkill, cls).list(
            skill_id=skill_id, user_id=user_id, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            modified_gt=modified_gt, modified_gte=modified_gte,
            modified_lt=modified_lt, modified_lte=modified_lte
        )
