import asyncio
from importlib.resources import read_text
from dataclasses import make_dataclass
from time import sleep

import pandas as pd
from pprint import pprint
from tqdm import tqdm
from uuid import uuid4

from rest_api.db import select, execute_select, execute_many
import toloka.queries as queries
from toloka.interface.toloka import Toloka
from toloka.interface.assignments import get_results, calc_overlap, get_results_xlsx
from toloka.interface.operation import Operation


STATUS = 'ACCEPTED'

sandbox = 1
pool = 'exam'

if sandbox:
    MODE = "sandbox"
    POOL_ID = "251555"
else:
    MODE = "main"
    if pool == 'exam':
        POOL_ID = "8823032"  # Exam
    if pool == 'reab':
        POOL_ID = "8823054"  # Reabilitation
    if pool == 'main':
        POOL_ID = "8823046"  # Main


def insert_result_to_db(rows, cols):
    values = [i + j for i, j in list(zip([(x[cols.index('TaskId')], ) for x in rows], rows))]
    execute_many(
        """
        BEGIN
           IF NOT EXISTS (SELECT * FROM FFValMarkup WHERE TaskId = ?)
           BEGIN
               INSERT INTO FFValMarkup ({cols}) VALUES ({placeholders})
           END
        END
        """.format(
            cols=','.join(cols),
            placeholders=','.join(['?'] * len(cols))
        ), values=values
    )


async def main():
    # rows, cols = await get_results(pool_id=POOL_ID, mode=MODE, status=STATUS)
    rows, cols = get_results_xlsx('~/Desktop/res1204.xlsx')
    vc = calc_overlap(rows, cols)
    print(vc)
    assert (vc.values > 1).sum() == 0
    insert_result_to_db(rows, cols)


if __name__ == '__main__':
    asyncio.run(main())
