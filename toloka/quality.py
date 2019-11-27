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
from toloka.interface import Toloka


@dataclass_json
@dataclass
class Condition:
    key: str
    operator: str
    value: float


@dataclass_json
@dataclass
class Action:
    type: str
    parameters: field(init=False)
    scope: InitVar[str]
    duration_days: InitVar[int] = None
    private_comment: InitVar[str] = None
    skill_id: InitVar[str] = None
    from_field: InitVar[str] = None
    skill_value: InitVar[int] = None

    def __post_init__(self, scope, duration_days, private_comment, skill_id, from_field, skill_value):
        self.parameters = SimpleNamespace(**{
            'scope': scope,
            'duration_days': duration_days,
            'private_comment': private_comment,
            'skill_id': skill_id,
            'from_field': from_field,
            'skill_value': skill_value
        })



@dataclass_json
@dataclass
class Rule:
    conditions: List[Condition]
    actions: List[Action]


@dataclass_json
@dataclass
class Config:
    collector_сonfig: field(init=False)
    rules: List[Rule]
    type: InitVar[str]
    history_size: InitVar[int] = None
    answer_threshold: InitVar[int] = None
    fast_submit_threshold_seconds: InitVar[int] = None

    def __post_init__(self, type, history_size, answer_threshold, fast_submit_threshold_seconds):
        parameters = SimpleNamespace(**{
            'history_size': history_size,
            'answer_threshold': answer_threshold,
            'fast_submit_threshold_seconds': fast_submit_threshold_seconds,
        })
        self.collector_сonfig = SimpleNamespace(**{
            'type': type,
            'parameters': parameters
        })


@dataclass_json
@dataclass
class QualityControl:
    config: List[Config]
    captcha_frequency: str = None
