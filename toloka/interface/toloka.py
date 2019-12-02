import asyncio
from importlib.resources import read_text

from aiohttp import ClientSession, TCPConnector, ClientTimeout
import simplejson as json

from rest_api.requests import request
import toloka
import toloka.configs as configs

def get_client_session(token):
    connector = TCPConnector()
    timeout = ClientTimeout(total=0)
    headers = {"Authorization": f"OAuth {token}"}
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
            print(self.data_class)
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

    async def create(self, params=None):
        if self.data is None:
            raise AttributeError('Object data is not set')
        url = self.__class__.host + self.__class__.endpoint
        try:
            data = self.data.to_dict()
        except AttributeError:
            data = [x.to_dict() for x in self.data]
        return await request(
            self.__class__.session, 'post', url=url,
            params=params,
            data=data
        )

    async def edit(self):
        if self.data is None:
            raise AttributeError('Object data is not set')
        url = self.__class__.host + self.__class__.endpoint + '/' + self.id
        return await request(
            self.__class__.session, 'put', url=url,
            params=None,
            data=self.data.to_dict()
        )

    async def get_data(self):
        if self.id is None:
            raise AttributeError('Object id is not set')
        url = self.__class__.host + self.__class__.endpoint + '/' + self.id
        data_dict = await request(self.__class__.session, 'get', url=url)
        self.data = self.__class__.data_class.from_dict(data_dict)

    async def save(self, filename):
        if self.data is None:
            raise AttributeError('Object data is not set')
        with open('./configs/' + filename, 'w', encoding='utf-8') as f:
            json.dump(self.data.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    async def list(cls, **kwargs):
        url = cls.host + cls.endpoint
        return await request(cls.session, 'get', url=url, params=kwargs)

    @classmethod
    async def get(cls, id):
        url = cls.host + cls.endpoint + '/' + id
        return await request(cls.session, 'get', url=url)

    @classmethod
    def init_session(cls, mode=None):
        cls.session = get_client_session(cls.token)
        if mode is not None:
            initialize_toloka(cls, mode)
        return cls.session
