from pprint import pprint
import simplejson as json
from types import SimpleNamespace
from collections import namedtuple
from typing import Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class A:
    a: SimpleNamespace

# Car = namedtuple('Car', [
#      'color',
#      'mileage',
# ])
# car = Car('red', 0)
# a = A(car)
# res = A.schema().dump(a)
# pprint(res)


from toloka.interface.pool import Pool

pool = Pool()
Pool.get_data()
