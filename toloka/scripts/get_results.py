import asyncio
from importlib.resources import read_text
from dataclasses import make_dataclass
from time import sleep

import pandas as pd
from pprint import pprint
from tqdm import tqdm
from uuid import uuid4

from rest_api.db import select, execute_select
import toloka.queries as queries
from toloka.interface.toloka import Toloka
from toloka.interface.assignments import Assignment
from toloka.interface.operation import Operation


async def get_results(pool_id):
    async with Toloka.init_session() as session:
        keys = ['doubt', 'error', 'result', 'image_left', 'image_right',
                'thumb_left1', 'thumb_left2', 'thumb_left3', 'thumb_right1',
                'thumb_right2', 'thumb_right3']
        result = await Assignment.list(pool_id=pool_id)
        rows = []
        for i in result['items']:
            if i['status'] in ['ACCEPTED', 'SUBMITTED']:
                for input_values, answer in zip(i['tasks'], i['solutions']):
                    rows.append(dict(
                        user_id=i['user_id'],
                        EventId1=int(input_values['input_values']['image_left'].split('.')[0]),
                        EventId2=int(input_values['input_values']['image_right'].split('.')[0]),
                        **answer['output_values']
                    ))
        return pd.DataFrame(rows)

def calc_overlap(df):
    df['index'] = df[['EventId1', 'EventId2']].apply(lambda x: frozenset((x['EventId1'], x['EventId2'])), axis=1)
    return df['index'].value_counts().sort_values()

if __name__ == '__main__':
    df = asyncio.run(get_results(Toloka.pool_id))
    print(calc_overlap(df))
    df.to_excel('C:/Users/Somov.A/Desktop/validation_markup.xlsx', index=False)
