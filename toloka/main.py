import asyncio
from importlib.resources import read_text
from collections import Counter
from dataclasses import make_dataclass
from time import sleep

import pandas as pd
from pprint import pprint
import simplejson as json
from tqdm import tqdm
from uuid import uuid4

from rest_api.db import select, execute_select
import toloka.configs as configs
from toloka.interface import Toloka
from toloka.task import Task, TaskData
from toloka.operation import Operation
from toloka.pool import Pool
from toloka.assignments import Assignment

# async def create_project():
DATE_START = '2019-09-12'
DATE_END = '2019-09-13'
CONF = 0.75


async def main():
    query1 = f"""
        WITH Idx AS (
        	SELECT DISTINCT Id
        	FROM FindFaceEvents f1 WITH (nolock)
        	WHERE f1.Store LIKE '107%' AND f1.CreatedDate BETWEEN '{DATE_START}' AND '{DATE_END}'
        ),

        ResultSet AS (
        	SELECT Id EventId1, m.EventId2 EventId2, m.Confidence
        	FROM Idx i
        		JOIN FFMatrix m WITH (nolock) ON Id=m.EventId1
        	UNION ALL
        	SELECT Id EventId1, m.EventId1 EventId2, m.Confidence
        	FROM Idx i
        		JOIN FFMatrix m WITH (nolock) ON Id=m.EventId2
        ),

        ResultSetRN AS (
        	SELECT
        		EventId1,
        		EventId2,
        		ROW_NUMBER() OVER (PARTITION BY EventId1 ORDER BY r.Confidence DESC, r.EventId2 ASC) RN
        	FROM ResultSet r
        )

        SELECT DISTINCT
        	EventId1,
        	EventId2,
        	RN
        INTO #ResultSet
        FROM ResultSetRN r
        WHERE EventId1 <> EventId2 AND RN < 4

        SELECT
        	EventId1,
        	MAX(CASE WHEN RN = 1 THEN EventId2 END) EventId2,
        	MAX(CASE WHEN RN = 2 THEN EventId2 END) EventId3
        INTO #Thumbs
        FROM #ResultSet r
        GROUP BY EventId1
        ORDER BY EventId1
        SELECT DISTINCT
    		IIF(m.EventId1 > m.EventId2, m.EventId1, m.EventId2) EventId1,
    		IIF(m.EventId1 > m.EventId2, m.EventId2, m.EventId1) EventId2
        INTO #Pairs
    	FROM FFMatrix m WITH(nolock)
    		JOIN FindFaceEvents f1 WITH (nolock) ON f1.Id=EventId1 AND f1.Store LIKE '107%' AND f1.CreatedDate BETWEEN '{DATE_START}' AND '{DATE_END}'
    		JOIN FindFaceEvents f2 WITH (nolock) ON f2.Id=EventId2 AND f2.Store LIKE '107%' AND f2.CreatedDate BETWEEN '{DATE_START}' AND '{DATE_END}'
    	WHERE m.Confidence > {CONF} AND EventId1 <> EventId2
    """
    query2 = """
        SELECT
            CONCAT(CAST(p.EventId1 AS varchar(max)), '.jpeg') image_left,
            CONCAT(CAST(p.EventId2 AS varchar(max)), '.jpeg') image_right,
            CONCAT(CAST(t1.EventId1 AS varchar(max)), '.jpg') thumb_left1,
            CONCAT(CAST(t1.EventId2 AS varchar(max)), '.jpg') thumb_left2,
            CONCAT(CAST(t1.EventId3 AS varchar(max)), '.jpg') thumb_left3,
            CONCAT(CAST(t2.EventId1 AS varchar(max)), '.jpg') thumb_right1,
            CONCAT(CAST(t2.EventId2 AS varchar(max)), '.jpg') thumb_right2,
            CONCAT(CAST(t2.EventId3 AS varchar(max)), '.jpg') thumb_right3
        FROM #Pairs p
            JOIN #Thumbs t1 ON t1.EventId1=p.EventId1
            JOIN #Thumbs t2 ON t2.EventId1=p.EventId2
    """
    res, cols = execute_select(query1, query2)

    InputValues = make_dataclass('InputValues', cols)

    tasks = [TaskData(input_values=InputValues(**dict(zip(cols, x))), pool_id=Toloka.pool_id) for x in res]
    task = Task(data=tasks)

    async with Toloka.init_session() as session:
        # result = await task.create(async_mode=True, allow_defaults=True, skip_invalid_items=False, operation_id=str(uuid4()))

        # operation_id = result['result']['id']
        # operation = await Operation.get(operation_id)
        operations = await Operation.list_operations(submitted_gt='2019-11-20T13:00:00')#, status='RUNNING')
        # while operation['progress'] < 100:
        while len(operations['items']) > 0:
            print(*[x['progress'] for x in operations['items']])
            # print(operation['progress'])
            sleep(30)
            operations = await Operation.list_operations(submitted_gt='2019-11-20T13:00:00', status='RUNNING')
        # pool = Pool(filename='pool.json')
        # await pool.edit()
        # print(await Pool.list())
        # pprint(await Pool().get_pool_properties('pool2.json'))

        # pprint(await Operation.list_operations(submitted_gt='2019-11-19T00:00:00'))
        # 399486aa-92d4-4b80-8764-d46a4bcf79de
        # pprint(await Operation.get_operation('8999f640-0f27-4cbf-b98f-0b873b784af3', True))

        # pool = Pool()
        # await pool.get_pool_properties(id=246756)
        # pool.id = 246756
        # pool.pool_data.defaults.default_overlap_for_new_tasks = 3
        # await pool.update_pool()
        pass


if __name__ == '__main__':
    df = asyncio.run(main())
