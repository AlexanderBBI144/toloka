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
from toloka.quality import Config, QualityControl


@dataclass_json
@dataclass
class TaskSpec:
    pass


@dataclass_json
@dataclass
class Project:
    public_name: str
    public_description: str
    task_spec: TaskSpec
    assignments_issuing_type: str
    public_instructions: str = None
    private_comment: str = None
    assignments_issuing_view_config: field(init=False) = None
    title_template: InitVar[str] = None
    description_template: InitVar[str] = None
    assignments_automerge_enabled: bool = None
    max_active_assignments_count: int = None
    quality_control: QualityControl = None
    id: str = None
    status: str = None
    created: str = None
