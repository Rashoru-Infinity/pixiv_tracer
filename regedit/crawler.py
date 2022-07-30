import asyncio
import json
from os import makedirs
from pathlib import Path

import aiofiles
import aiohttp

from .config import Config


class Crawler():
    def __init__(self, config_file_path='config.json'):
        self.config_file_path = config_file_path
        self.loop = asyncio.get_event_loop()
        self.session = None
        self.config = None
        self.cookie = {}
        self.users = {}

    def main(self):
        self.load_config()
        try:
            makedirs(self.config.cache_dir, exist_ok=True)
        except FileExistsError:
            # TODO: 同名のファイルがある場合適当にリネームするとか
            raise FileExistsError

        self.loop.create_task(self._main())
        self.loop.run_forever()

    def load_config(self):
        try:
            _config = Config(self.config_file_path)
            _config.load_config()
        except Exception as _e:
            print(_e)
            exit(1)

        self.config = _config

        for i in self.config.users:
            self.users[i['id']] = i
            self.users[i['id']]['likes'] = -1

    async def _main(self):
        if not self.session:
            self.session = aiohttp.ClientSession(loop=self.loop)
        if not self.cookie:
            self.cookie = self.login()

        for i in self.users:
            await self.do_main(i)

        print('push task')
        await asyncio.sleep(self.config.interval)
        self.loop.create_task(self._main())

    async def do_main(self, user):
        ret = await self.fetch(user)
        if ret['error']:
            print(f'fuck {self.users[user]["name"]}/ {ret["message"]}')
            exit(1)

        if self.users[user]['likes'] == -1:
            self.users[user]['likes'] = ret['body']['total']
            return

        _diff = ret['body']['total'] - self.users[user]['likes']
        if not _diff:
            return

        self.users[user]['likes'] = ret['body']['total']

        # TODO: 48枚以上とれるようにする．
        _posts = ret['body']['works'][:_diff]
        for p in _posts:
            await self.post(p)

    def login(self):
        # ここにログイン処理を書く．実装できないのでひとまずコンフィグのcookieを返す．
        return self.config.cookie

    async def fetch(self, id):
        _endpoint = (f'https://www.pixiv.net/ajax/user/{id}/illusts/bookmarks?' +
                     'tag=&offset=0&limit=48&rest=show&lang=ja')
        _header = {
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

        async with self.session.get(_endpoint, cookies=self.cookie, headers=_header) as ret:
            if ret.status != 200:
                exit(1)
            try:
                return json.loads(await ret.text())
            except json.JSONDecodeError:
                print('fuck JSONDecodeError')
                return {}
            except Exception as _e:
                print(_e)
                exit(1)

    async def get_thumbnail(self, endpoint: str):
        _header = {
            "referer": "https://www.pixiv.net/",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

        # TODO: cache dir の検索
        _filename = endpoint.split('/')[-1]

        async with self.session.get(endpoint, headers=_header) as img:
            if img.status != 200:
                print(f'fuck {img.status}')
                exit(1)

            async with aiofiles.open(Path(self.cache_dir, _filename), mode='wb') as f:
                await f.write(await img.read())

    async def post(self, message: dict = {}):
        _payload = self.enclose_packet(f'オススメ: {message["title"]}')
        _header = {'Content-Type': 'application/json'}

        # TODO: retcode
        await self.session.post(self.config.webhook_endpoint,
                                headers=_header, data=_payload)

    def enclose_packet(self, message):
        if self.config.webhook_type == 'discord':
            return json.dumps({"content": message})
        elif self.config.webhook_type == 'slack':
            return json.dumps({'text': message})
