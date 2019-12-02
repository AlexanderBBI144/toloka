import asyncio
from dataclasses import dataclass, field, make_dataclass
from dataclasses_json import dataclass_json, config
from importlib.resources import read_text
from typing import Any, List, Optional, Union

import simplejson as json
from uuid import uuid4

from rest_api.requests import request
import toloka.configs as configs
from toloka.interface.toloka import Toloka
from toloka.interface.quality import Config

@dataclass_json
@dataclass
class DynamicPricingConfigInterval:
    reward_per_assignment: float
    interval_from: int = field(
        default = None,
        metadata=config(
            field_name='from'
        )
    )
    interval_to: int = field(
        default = None,
        metadata=config(
            field_name='to'
        )
    )

@dataclass_json
@dataclass
class DynamicPricingConfig:
    type: str
    skill_id: str
    intervals: List[DynamicPricingConfigInterval]

@dataclass_json
@dataclass
class AssignmentsIssuingConfig:
    issue_task_suites_in_creation_order: bool = None


@dataclass_json
@dataclass
class DynamicOverlapConfigField:
    name: str


@dataclass_json
@dataclass
class DynamicOverlapConfig:
    type: str
    max_overlap: int
    min_confidence: float
    answer_weight_skill_id: str
    fields: List[DynamicOverlapConfigField]


@dataclass_json
@dataclass
class Defaults:
    default_overlap_for_new_task_suites: int
    default_overlap_for_new_tasks: int = None


@dataclass_json
@dataclass
class TaskDistributionFunctionInterval:
    interval_from: int = field(
        metadata=config(
            field_name='from'
        )
    )
    interval_to: int = field(
        metadata=config(
            field_name='to'
        )
    )
    intervals_frequency: int


@dataclass_json
@dataclass
class TaskDistributionFunction:
    scope: str
    distribution: str
    window_days: int
    intervals: List[TaskDistributionFunctionInterval]


@dataclass_json
@dataclass
class TrainingRequirement:
    training_pool_id: str = None
    training_passing_skill_value: str = None


@dataclass_json
@dataclass
class CheckpointsConfig:
    target_overlap: int
    task_distribution_function: TaskDistributionFunction


@dataclass_json
@dataclass
class RealSettings:
    real_settings: CheckpointsConfig


@dataclass_json
@dataclass
class QualityControlPool:
    training_requirement: TrainingRequirement = None
    captcha_frequency: str = None
    configs: List[Config] = None
    checkpoints_config: RealSettings = None


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
class FilterConditions:
    filter_or: List[FilterCondition] = field(
        metadata=config(
            field_name='or'
        )
    )


@dataclass_json
@dataclass
class Filter:
    filter_and: List[Union[FilterCondition, FilterConditions]] = field(
        metadata=config(
            field_name='and'
        )
    )


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
    filter: Filter = None
    quality_control: QualityControlPool = None
    dynamic_overlap_config: DynamicOverlapConfig = None
    mixer_config: MixerConfig = None
    id: str = None
    owner: Owner = None
    type: str = None
    status: str = None
    created: str = None


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
