import asyncio
from dataclasses import dataclass, field, InitVar
from dataclasses_json import dataclass_json
from importlib.resources import read_text
from types import SimpleNamespace
from typing import Any, List

import simplejson as json
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface import Toloka
from toloka.quality import Config


@dataclass_json
@dataclass
class DynamicPricingConfig:
    type: str
    skill_id: str
    intervals: field(init=False)
    intervals_from: InitVar[int] = None
    intervals_to: InitVar[int] = None
    intervals_reward_per_assignment: InitVar[float] = None

    def __post_init__(self, intervals_from, intervals_to, intervals_reward_per_assignment):
        self.intervals = SimpleNamespace(**{
            'from': intervals_from,
            'to': intervals_to,
            'reward_per_assignment': intervals_reward_per_assignment
        })


@dataclass_json
@dataclass
class AssignmentsIssuingConfig:
    issue_task_suites_in_creation_order: bool = None


@dataclass_json
@dataclass
class DynamicOverlapConfig:
    type: str
    max_overlap: int
    min_confidence: float
    answer_weight_skill_id: str
    fields: field(init=False)
    fields_name: InitVar[str]

    def __post_init__(self, fields_name):
        self.fields = SimpleNamespace(name=fields_name)


@dataclass_json
@dataclass
class Defaults:
    default_overlap_for_new_task_suites: int
    default_overlap_for_new_tasks: int = None


@dataclass_json
@dataclass
class TaskDistributionFunction:
    scope: str
    distribution: str
    window_days: int
    intervals: field(init=False)
    intervals_from: InitVar[int]
    intervals_to: InitVar[int]
    intervals_frequency: InitVar[int]

    def __post_init__(self, intervals_from, intervals_to, intervals_frequency):
        self.intervals = SimpleNamespace(**{
            'from': intervals_from,
            'to': intervals_to,
            'frequency': intervals_frequency
        })


@dataclass_json
@dataclass
class CheckpointsConfig:
    target_overlap: int
    task_distribution_function: TaskDistributionFunction


@dataclass_json
@dataclass
class QualityControlPool:
    training_requirement: field(init=False)
    checkpoints_config: field(init=False)
    captcha_frequency: str = None
    configs: List[Config] = None
    training_pool_id: InitVar[str] = None
    training_passing_skill_value: InitVar[int] = None
    real_settings: InitVar[CheckpointsConfig] = None

    def __post_init__(self, training_pool_id, training_passing_skill_value, real_settings):
        self.training_requirement = SimpleNamespace(**{
            'training_pool_id': training_pool_id,
            'training_passing_skill_value': training_passing_skill_value
        })
        self.checkpoints_config = SimpleNamespace(**{
            'real_settings': real_settings
        })


@dataclass_json
@dataclass
class MixerConfig:
    real_tasks_count: int
    golden_tasks_count: int
    training_tasks_count: int
    min_real_tasks_count: int = None
    min_golden_tasks_count: int = None
    min_training_tasks_count: int = None
    force_last_assignment: bool = None
    force_last_assignment_delay_seconds: int = None
    mix_tasks_in_creation_order: bool = None
    shuffle_tasks_in_task_suite: bool = None
    golden_task_distribution_function: TaskDistributionFunction = None
    training_task_distribution_function: TaskDistributionFunction = None


@dataclass_json
@dataclass
class Owner:
    id: str
    myself: bool


@dataclass_json
@dataclass
class FilterCondition:
    category: str
    key: str
    operator: str
    value: Any


@dataclass_json
@dataclass
class PoolData:
    project_id: str
    private_name: str
    may_contain_adult_content: bool
    will_expire: str
    reward_per_assignment: float
    assignment_max_duration_seconds: int
    defaults: Defaults
    private_comment: str = None
    public_description: str = None
    auto_close_after_complete_delay_seconds: int = None
    dynamic_pricing_config: DynamicPricingConfig = None
    auto_accept_solutions: bool = None
    assignments_issuing_config: AssignmentsIssuingConfig = None
    priority: int = None
    filter: field(init=False) = None
    quality_control: QualityControlPool = None
    dynamic_overlap_config: DynamicOverlapConfig = None
    mixer_config: MixerConfig = None
    id: str = None
    owner: Owner = None
    type: str = None
    status: str = None
    created: str = None
    filter_conditions: InitVar[List[FilterCondition]] = None

    def _create_or(self, conditions):
        if len(conditions) > 1:
            return SimpleNamespace(**{
                "or": conditions
            })
        else:
            return conditions[0]

    def _create_and(self, condition_groups):
        if len(condition_groups) > 1:
            return SimpleNamespace(**{
                "and": [self._create_or(x) for x in condition_groups]
            })
        else:
            return self._create_or(condition_groups[0])

    def __post_init__(self, filter_conditions):
        condition_groups = {}
        for fc in filter_conditions:
            condition_groups.setdefault(fc.category, []).append(fc)
        self.filter = self._create_and(list(condition_groups.values()))



class Pool(Toloka):
    endpoint = '/pools'
    data_class = PoolData

    def __init__(self, id=None, pool_data=None, filename=None):
        super(Pool, self).__init__(id, pool_data, filename)
        self.id = self.__class__.pool_id if self.id is None else self.id

    @classmethod
    async def list(cls, status=None, project_id=None, limit=None, sort='-created',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None,
                   last_started_gt=None, last_started_gte=None,
                   last_started_lt=None, last_started_lte=None):
        return await super(Pool, cls).list(
            status=status, project_id=project_id, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte,
            last_started_gt=last_started_gt, last_started_gte=last_started_gte,
            last_started_lt=last_started_lt, last_started_lte=last_started_lte
        )
