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
from toloka.interface import Toloka, Config, QualityControl


@dataclass_json
@dataclass
class InputOutputSpec:
    type: str
    required: bool = None
    hidden: bool = None
    min_value: float = None
    max_value: float = None
    allowed_values: List[Any] = None
    min_length: int = None
    max_length: int = None
    current_location: str = None


@dataclass_json
@dataclass
class Assets:
    script_urls: List[str] = None
    style_urls: List[str] = None


@dataclass_json
@dataclass
class Settings:
    showTimer: bool = None
    showTitle: bool = None
    showInstructions: bool = None
    showFullscreen: bool = None
    showSubmit: bool = None
    showSkip: bool = None
    showFinish: bool = None
    showMessage: bool = None


@dataclass_json
@dataclass
class ViewSpec:
    markup: str
    script: str
    styles: str
    settings: Settings
    assets: Assets = None


@dataclass_json
@dataclass
class TaskSpec:
    input_spec: 'InputSpec'
    output_spec: 'OutputSpec'
    view_spec: ViewSpec


@dataclass_json
@dataclass
class AssignmentsIssuingViewConfig:
    title_template: str
    description_template: str


@dataclass_json
@dataclass
class ProjectData:
    public_name: str
    public_description: str
    task_spec: TaskSpec
    assignments_issuing_type: str
    public_instructions: str = None
    private_comment: str = None
    assignments_issuing_view_config: AssignmentsIssuingViewConfig = None
    assignments_automerge_enabled: bool = None
    max_active_assignments_count: int = None
    quality_control: QualityControl = None
    id: str = None
    status: str = None
    created: str = None


class Project(Toloka):
    endpoint = '/projects'
    data_class = ProjectData

    @classmethod
    async def list(cls, status=None, limit=None, sort='id',
                   id_gt=None, id_gte=None, id_lt=None, id_lte=None,
                   created_gt=None, created_gte=None,
                   created_lt=None, created_lte=None):
        return await super(Project, cls).list(
            status=status, limit=limit, sort=sort,
            id_gt=id_gt, id_gte=id_gte, id_lt=id_lt, id_lte=id_lte,
            created_gt=created_gt, created_gte=created_gte,
            created_lt=created_lt, created_lte=created_lte
        )
