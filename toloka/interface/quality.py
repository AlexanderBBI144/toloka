import asyncio
from dataclasses import dataclass, field, InitVar
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace
from typing import List

import simplejson as json
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface.toloka import Toloka


@dataclass_json
@dataclass
class ActionParameters:
    scope: str
    duration_days: int = None
    private_comment: str = None
    skill_id: str = None
    from_field: str = None
    skill_value: int = None


@dataclass_json
@dataclass
class Action:
    type: str
    parameters: ActionParameters


@dataclass_json
@dataclass
class Condition:
    key: str
    operator: str
    value: float


@dataclass_json
@dataclass
class Rule:
    conditions: List[Condition]
    actions: List[Action]


@dataclass_json
@dataclass
class CollectorConfigParameters:
    history_size: int = None
    answer_threshold: int = None
    fast_submit_threshold_seconds: int = None


@dataclass_json
@dataclass
class CollectorConfig:
    type: str
    parameters: CollectorConfigParameters


@dataclass_json
@dataclass
class Config:
    collector_сonfig: CollectorConfig
    rules: List[Rule]


@dataclass_json
@dataclass
class QualityControl:
    configs: List[Config]
    captcha_frequency: str = None
