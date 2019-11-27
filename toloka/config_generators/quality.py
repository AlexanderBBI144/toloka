import asyncio
from importlib.resources import read_text
from collections import Counter
from time import sleep

import pandas as pd
from pprint import pprint
import simplejson as json
from tqdm import tqdm

from rest_api.db import select
import toloka.configs as configs
from toloka.interface import Toloka
from toloka.task import Task
from toloka.operation import Operation
from toloka.pool import Pool
from toloka.quality import QualityControl, Config, Rule, Condition, Action

# Заполнить skill_id во ВСЕХ golden_set_rules и fast_submit_threshold_seconds
# Проставить skill_id, assignment_max_duration_seconds, training_pool_id,
# answer_weight_skill_id в конфигурациях пулов


def create_quality_rules():
    golden_set_rules = [
        Rule(
            conditions=[
                Condition(
                    key="golden_set_answers_count",
                    operator="GTE",
                    value=50
                ),
                Condition(
                    key="golden_set_correct_answers_rate",
                    operator="GTE",
                    value=i * 5
                ),
                Condition(
                    key="golden_set_correct_answers_rate",
                    operator="LT",
                    value=(i + 1) * 5
                ),
            ],
            action=Action(
                type="SET_SKILL",
                skill_id=,
                skill_value=i * 5
            )
        )
        for i in range(20)
    ]

    golden_set_rules.append(
        Rule(
            conditions=[
                Condition(
                    key="golden_set_answers_count",
                    operator="GTE",
                    value=50
                ),
                Condition(
                    key="golden_set_correct_answers_rate",
                    operator="EQ",
                    value=100
                ),
            ],
            action=Action(
                type="SET_SKILL",
                skill_id=,
                skill_value=100
            )
        )
    )

    golden_set_rules.append(
        Rule(
            conditions=[
                Condition(
                    key="golden_set_answers_count",
                    operator="GTE",
                    value=50
                ),
            ],
            action=Action(
                type="SET_SKILL_FROM_OUTPUT_FIELD",
                skill_id=,
                from_field="correct_answers_rate"
            )
        )
    )

    majority_vote_rules = [
        Rule(
            conditions=[
                Condition(
                    key="total_answers_count",
                    operator="GTE",
                    value=50
                ),
                Condition(
                    key="correct_answers_rate",
                    operator="LT",
                    value=25
                )
            ],
            action=Action(
                type="RESTRICTION",
                scope="PROJECT",
                duration_days=10,
                private_comment="Ответы не совпали с мнением большинства."
            )
        )
    ]

    captcha_rules = [
        Rule(
            conditions=[
                Condition(
                    key="stored_results_count",
                    operator="EQ",
                    value=10
                ),
                Condition(
                    key="success_rate",
                    operator="LTE",
                    value=70
                )
            ],
            action=Action(
                type="RESTRICTION",
                scope="PROJECT",
                duration_days=2,
                private_comment="Неверно ввел капчу."
            )
        )
    ]

    assignment_submit_time_rules = [
        Rule(
            conditions=[
                Condition(
                    key="total_submitted_count",
                    operator="EQ",
                    value=10
                ),
                Condition(
                    key="fast_submitted_count",
                    operator="GTE",
                    value=4
                )
            ],
            actions=Action(
                type="RESTRICTION",
                scope="PROJECT",
                duration_days=1,
                private_comment="Более 4 быстрых ответов"
            )
        )
    ]

    quality_control = QualityControl(
        captcha_frequency="MEDIUM",
        configs=[
            Config(
                type='GOLDEN_SET',
                history_size=1000,
                rules=golden_set_rules
            ),
            Config(
                type='MAJORITY_VOTE',
                history_size=100,
                answer_threshold=3,
                rules=majority_vote_rules
            ),
            Config(
                type='CAPTCHA',
                history_size=10,
                rules=captcha_rules
            ),
            Config(
                type='ASSIGNMENT_SUBMIT_TIME',
                history_size=10,
                fast_submit_threshold_seconds=,
                rules=captcha_rules
            ),
        ]
    )
    return quality_control
