import asyncio
import os
from importlib.resources import read_text

from aiohttp import ClientSession, TCPConnector, ClientTimeout
from pprint import pprint
import simplejson as json
from tqdm import tqdm

from rest_api.requests import request
import toloka
import toloka.configs as configs


def get_client_session(token):
    connector = TCPConnector()
    timeout = ClientTimeout(total=0)
    headers = {"Authorization": f"OAuth {token}", "Content-Type": "application/json"}
    return ClientSession(connector=connector, timeout=timeout, headers=headers)


def initialize_toloka(self, mode=None):
    config = json.loads(read_text(toloka, 'config.json'))
    self.mode = config['mode'] if mode is None else mode
    config = config[self.mode]
    self.token = config['token']
    self.project_id = config.get('project_id', None)
    self.pool_id = config.get('pool_id', None)
    if self.mode == 'sandbox':
        self.host = 'https://sandbox.toloka.yandex.ru/api/v1'
    elif self.mode == 'main':
        self.host = 'https://toloka.yandex.ru/api/v1'
    else:
        raise AttributeError("Mode must be one of the following: 'sandbox', 'main'")


class TolokaMeta(type):
    def __init__(self, name, bases, attrs):
        initialize_toloka(self)


class Toloka(metaclass=TolokaMeta):
    def __init__(self, id=None, data=None, filename=None):
        if filename is not None:
            data = read_text(configs, filename)
            self.data = self.data_class.schema().loads(data)
        else:
            self.data = data
        if id is None:
            try:
                self.id = self.data.id
            except:
                self.id = id
        else:
            self.id = id
        try:
            self.data.project_id = Toloka.project_id
        except AttributeError:
            pass

    async def create(self, params=None):
        if self.data is None:
            raise AttributeError('Object data is not set')
        url = Toloka.host + self.__class__.endpoint
        try:
            data = self.data.to_dict()
        except AttributeError:
            data = [x.to_dict() for x in self.data]
        return await request(
            Toloka.session, 'post', url=url,
            params=params,
            data=data
        )

    async def edit(self):
        if self.data is None:
            raise AttributeError('Object data is not set')
        url = Toloka.host + self.__class__.endpoint + '/' + self.id
        return await request(
            Toloka.session, 'put', url=url,
            params=None,
            data=self.data.to_dict()
        )

    async def get_data(self):
        if self.id is None:
            raise AttributeError('Object id is not set')
        url = Toloka.host + self.__class__.endpoint + '/' + self.id
        data_dict = await request(Toloka.session, 'get', url=url)
        # pprint(self.__class__.data_class)
        # pprint(data_dict)
        self.data = self.__class__.data_class.from_dict(data_dict)

    async def save(self, filename):
        if self.data is None:
            raise AttributeError('Object data is not set')
        config_dir = os.path.dirname(os.path.abspath(configs.__file__))
        with open(config_dir + '/' + filename, 'w+', encoding='utf-8') as f:
            json.dump(self.data.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    async def list(cls, **kwargs):
        url = Toloka.host + cls.endpoint
        result = await request(Toloka.session, 'get', url=url, params=kwargs)
        try:
            return result['items']
        except KeyError:
            print(result)

    @classmethod
    async def list_all(cls, **kwargs):
        url = Toloka.host + cls.endpoint
        last_id = None
        result = {'has_more': True}
        items = []
        with tqdm() as pbar:
            while result['has_more']:
                params = dict(sort='id', limit=cls.max_limit, id_gt=last_id, **kwargs)
                result = await request(Toloka.session, 'get', url=url, params=params)
                # print(result)
                items.extend(result['items'])
                last_id = result['items'][-1]['id']
                pbar.update()
        return items

    @classmethod
    async def get(cls, id):
        url = Toloka.host + cls.endpoint + '/' + id
        return await request(Toloka.session, 'get', url=url)

    @classmethod
    async def patch(cls, id, params=None, data=None):
        url = Toloka.host + cls.endpoint + '/' + id
        return await request(Toloka.session, 'patch', url=url, params=params, data=data)

    @classmethod
    def init_session(cls, mode=None):
        if mode is not None:
            initialize_toloka(cls, mode)
        cls.session = get_client_session(cls.token)
        return cls.session
