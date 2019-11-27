import asyncio
from importlib.resources import read_text

from aiohttp import ClientSession, TCPConnector, ClientTimeout
import simplejson as json

import toloka.configs as configs

def get_client_session(token):
    connector = TCPConnector()
    timeout = ClientTimeout(total=0)
    headers = {"Authorization": f"OAuth {token}"}
    return ClientSession(connector=connector, timeout=timeout, headers=headers)


class Toloka(type):

    token = ''
    session = None

    @classmethod
    def init(cls):
        config = json.loads(read_text(configs, 'config.json'))
        cls.token = config['token']
        cls.mode = config['mode']
        cls.project_id = config['project_id']
        cls.pool_id = config['pool_id']
        cls.session = get_client_session(cls.token)
        return cls.session

    def __init__(self, a, b, c):
        print(a, b, c)
        pass

    async def create(self):
        if self.data is None:
            raise AttributeError('Object data is not set')
        url = self.__class__.host + self.__class__.endpoint
        return await request(
            self.__class__.session, 'post', url=url,
            params=None,
            data=self.data.to_dict()
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
        url = self.__class__.host + self.__class__.endpoint + '/' + self.id
        data_dict = await request(self.__class__.session, 'get', url=url)
        self.data = self.dataclass.from_dict(data_dict)

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

    @property
    def host(cls):
        if cls.mode == 'sandbox':
            return 'https://sandbox.toloka.yandex.ru/api/v1'
        elif cls.mode == 'main':
            return 'https://toloka.yandex.ru/api/v1'
        else:
            raise AttributeError('Mode is not set.')

    @host.setter
    def host(cls, value):
        cls._host = value

    @property
    def mode(cls):
        return cls._mode

    @mode.setter
    def mode(cls, value):
        if value not in ('sandbox', 'main'):
            raise ValueError("Mode must be 'sandbox' or 'main'")
        cls._mode = value

    @property
    def project(cls):
        return cls._project

    @project.setter
    def project(cls, value):
        cls._project = value

    @property
    def pool(cls):
        return cls._pool

    @pool.setter
    def pool(cls, value):
        cls._pool = value
