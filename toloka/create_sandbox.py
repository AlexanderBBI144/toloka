import asyncio
from dataclasses import make_dataclass
from importlib.resources import read_text
import logging
import warnings

from dataclasses_json import dataclass_json
from pprint import pprint

from rest_api.db import select
from toloka.interface import Toloka, Pool, Project, InputOutputSpec, Skill, Task, create_tasks
from toloka.load_missing_faces import load_missing_faces
from toloka.quality_generator import create_quality_rules
import toloka.queries as queries
from toloka.utils import batch


warnings.filterwarnings("ignore", module="dataclasses_json")


logging.basicConfig(
    # filename='./log/main_sandbox.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


async def get_project_id(name):
    project_list = [x for x in await Project.list()
                    if x['public_name'] == name and x['status'] != 'ARCHIVED']
    try:
        project_id = project_list[0]['id']
    except IndexError:
        project = Project(filename='project_template.json')
        await project.create()
        await project.save()
        project_id = project.data.id
        raise
    return project_id


async def get_skills():
    skill_names = [
        'Сравнение лиц людей - training',
        'Сравнение лиц людей - proxy',
        'Сравнение лиц людей - основной'
    ]
    filenames = {
        'Сравнение лиц людей - proxy': 'skill_proxy.json',
        'Сравнение лиц людей - основной': 'skill_exact.json'
    }
    skill_ids = {}
    for skill_name in skill_names:
        skill_list = await Skill.list(name=skill_name)
        try:
            skill_ids[skill_name] = skill_list[0]['id']
        except IndexError:
            skill = Skill(filename=filenames[skill_name])
            await skill.create()
            await skill.save()
            skill_ids[skill_name] = skill.data.id
    return skill_ids


async def update_project(project_id, skill_ids):
    skill_proxy_id = skill_ids['Сравнение лиц людей - proxy']
    skill_main_id = skill_ids['Сравнение лиц людей - основной']
    project = Project(id=project_id)
    await project.get_data()
    project.data.quality_control = create_quality_rules(skill_proxy_id, skill_main_id)
    await project.edit()
    return project


async def get_pool(project_id, filename):
    pool = Pool(filename=filename)
    pool.data.project_id = project_id
    return pool


async def get_train_id(project_id):
    pool_list = await Pool.list(project_id=project_id)
    return [x for x in pool_list if x['type'] == 'TRAINING' and
                                    x['status'] != 'ARCHIVED'][0]['id']


async def set_pool_params(pool_types, train_id, skill_ids):
    main_count = len([pool_type for pool_type, pool in pool_types if pool_type == 'main'])
    main_pool_idx = 1
    for pool_type, pool in pool_types:
        if main_count > 1 and pool_type == 'main':
            pool.data.private_name += f' {main_pool_idx}'
            main_pool_idx += 1
        pool.data.quality_control.training_requirement.training_pool_id = train_id
        try:
            pool.data.dynamic_pricing_config.skill_id = skill_ids['Сравнение лиц людей - proxy']
        except AttributeError:
            logger.info(f"{pool.data.private_name} нет атрибута skill_id в quality_control")
        try:
            for a in pool.data.filter.filter_and:
                for o in a.filter_or:
                    if o.category == 'skill':
                        o.key = skill_ids['Сравнение лиц людей - основной']
        except AttributeError:
            logger.info(f"{pool.data.private_name} нет атрибута skill_id в filter")
        try:
            pool.data.dynamic_overlap_config.answer_weight_skill_id = skill_ids['Сравнение лиц людей - основной']
        except AttributeError:
            logger.info(f"{pool.data.private_name} нет атрибута skill_id в dynamic_overlap_config")
    return [pool for pool_type, pool in pool_types]


async def update_pools(project_id, pool_types):
    main_count = len([pool_type for pool_type, pool in pool_types if pool_type == 'main'])
    main_pool_idx = 1
    pool_list = await Pool.list(project_id=project_id)
    existing_pools = [x['private_name'] for x in pool_list if x['status'] != 'ARCHIVED']
    pool_ids = {x['private_name']: x['id'] for x in pool_list if x['status'] != 'ARCHIVED'}
    for pool_type, pool in pool_types:
        pool.data.project_id = project_id
        if pool.data.private_name not in existing_pools:
            if main_count > 1 and pool_type == 'main':
                pool.data.private_name += f' {main_pool_idx}'
                main_pool_idx += 1
            await pool.create()
            await pool.save()
        else:
            pool.id = pool_ids[pool.data.private_name]
            await pool.edit()


async def create_pool_tasks(pool_scripts):
    rows_list = []
    for pool_type, (query, pool_ids) in pool_scripts.items():
        logger.info('Read query')
        rows, cols = select(query)
        logger.info('Fetch rows')
        known_solutions_cols = ['result']
        annotation_col = 'message_on_unknown_solution'
        for batch_pool, pool_id in zip(batch(rows, batch_number=len(pool_ids)), pool_ids):
            for b in batch(batch_pool, batch_size=100000):
                await create_tasks(
                    pool_id=pool_id, rows=b, cols=cols,
                    known_solutions_cols=known_solutions_cols,
                    annotation_col=annotation_col
                )
                logger.info(f'Create tasks {pool_id}: {len(b)}')
        rows_list.extend(rows)
    return rows_list, cols


async def upload_faces(mode, rows, cols):
    frame_cols = ['image_left', 'image_right']
    face_cols = ['thumb_left1', 'thumb_left2', 'thumb_left3',
                 'thumb_right1', 'thumb_right2', 'thumb_right3']
    await load_missing_faces(
        mode=mode,
        rows=rows,
        cols=cols,
        frame_cols=frame_cols,
        face_cols=face_cols
    )


async def main():
    mode = 'main'
    name = 'Сравнение лиц людей'
    train_id = "9044519" if mode == 'main' else "257164"
    update_train = True
    pool_filenames = [
        # ('exam', 'pool_exam_template.json'),
        # ('eval', 'pool_eval_template.json'),
        # ('main', 'pool_main_template.json'),
        # ('main', 'pool_main_template.json'),
        # ('main', 'pool_main_template.json'),
        # ('main', 'pool_main_template.json'),
        # ('main', 'pool_main_template.json'),
        # ('reab', 'pool_reab_template.json')
    ]
    task_create_queries = dict(
        train="exec spFFCreateTasksTrain",
        exam="exec spFFCreateTasksVal @exam=1, @count=200" if mode == 'main' else
             "exec spFFGetDataTest @mode='exam'",
        eval="""
             exec spFFCreateTasksEval @count=100
             exec spFFCreateTasksVal @exam=0, @count=10
             """ if mode == 'main' else
             "exec spFFGetDataTest @mode='eval'",
        main="""
             exec spFFCreateTasksMain
                 @date_start='2019-10-01',
                 @date_end='2019-11-01',
                 @camera=NULL,
                 @threshold=0.77,
                 @min_quality=-1000,
                 @top_limit=10
             exec spFFCreateTasksVal @exam=0, @count=800
             """ if mode == 'main' else
             "exec spFFGetDataTest @mode='main'",
        reab="exec spFFCreateTasksVal @exam=1, @count=200" if mode == 'main' else
             "exec spFFGetDataTest @mode='eval'"
    )

    async with Toloka.init_session(mode):
        logger.info('Get project id')
        project_id = await get_project_id(name)

        logger.info('Get skills')
        skill_ids = await get_skills()

        logger.info('Update project')
        project = await update_project(project_id, skill_ids)

        logger.info('Get pools')
        pool_types = []
        pools = []
        for pool_type, filename in pool_filenames:
            pool = await get_pool(project_id, filename)
            pools.append(pool)
            pool_types.append((pool_type, pool))

        logger.info('Set set_pool_params')
        pools = await set_pool_params(pool_types, train_id, skill_ids)

        logger.info('Update pools')
        await update_pools(project_id, pool_types)

        logger.info('Create pool tasks')
        pool_scripts = {}
        for pool_type, pool in pool_types:
            pool_scripts.setdefault(pool_type, [task_create_queries[pool_type], []])[1].append(pool.data.id)
        if update_train:
            pool_scripts['train'] = (task_create_queries['train'], [train_id])
        rows, cols = await create_pool_tasks(pool_scripts)

        # logger.info('Upload faces')
        # await upload_faces(mode, rows, cols)

if __name__ == '__main__':
    asyncio.run(main())
