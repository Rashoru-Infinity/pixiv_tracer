import asyncio
import json

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

        await asyncio.sleep(self.config.interval)
        self.loop.create_task(self._main())

    async def do_main(self, user_id):
        ret = await self.fetch(user_id)
        if ret['error']:
            print(f'fuck {self.users[user_id]["name"]}/ {ret["message"]}')
            exit(1)

        if self.users[user_id]['likes'] == -1:
            self.users[user_id]['likes'] = ret['body']['total']
            return

        _diff = ret['body']['total'] - self.users[user_id]['likes']
        if _diff < 0:
            return

        self.users[user_id]['likes'] = ret['body']['total']

        # TODO: 48枚以上とれるようにする．
        _posts = ret['body']['works'][:_diff]
        for p in _posts:
            p['recommended_by'] = self.users[user_id]['name']
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
                print(f'GET fucked: {ret.status}')
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

        async with self.session.get(endpoint, headers=_header) as img:
            if img.status != 200:
                print(f'fuck {img.status}')
                return None

            return await img.read()

    async def post(self, message: dict = {}):
        _payload = await self.enclose_packet(message)

        async with self.session.post(self.config.webhook_endpoint, data=_payload) as ret:
            if not ret.status in [200, 204]:
                print(f'POST fucked: {ret.status}')
                print(f'_payload: {_payload}')

    async def enclose_packet(self, message):
        if self.config.webhook_type == 'discord':
            _payload = {
                'embeds': [
                    {
                        'author': {
                            'name': 'pixiv',
                            'url': 'https://pixiv.net',
                            'icon_url': 'https://pbs.twimg.com/profile_images/' +
                            '1049908233865977858/OLhsoKB6_400x400.jpg'
                        },
                        'title': f'{message["recommended_by"]}さんのオススメのイラストです!\n',
                        'description': f'[{message["title"]}]' +
                        f'(https://www.pixiv.net/artworks/{message["id"]})\n\n',
                        'color': 2073595,
                        'thumbnail': {
                            'url': 'attachment://thumbnail.jpg'
                        },
                        'footer': {
                            'text': 'regedit (https://github.com/enjoydolylab/regedit)'
                        },
                        'fields': [
                            {
                                'name': 'イラストレーター',
                                'value': message['userName'],
                                'inline': False
                            },
                            {
                                'name': 'Tag',
                                'value': message['tags'][0],
                                'inline': True
                            }
                        ]
                    }
                ]
            }

            for i in range(1, 6) if len(message['tags']) > 6 else range(1, len(message['tags'])):
                _payload['embeds'][0]['fields'].append(
                    {
                        'name': '\u200B',
                        'value': message['tags'][i],
                        'inline': True
                    }
                )

            _form = aiohttp.FormData()
            _form.add_field('payload_json', json.dumps(_payload))
            _file = await self.get_thumbnail(message['url'])
            if _file:
                _form.add_field('file',
                                _file,
                                filename='thumbnail.jpg',
                                content_type='image/jpeg')
            return _form
        elif self.config.webhook_type == 'slack':
            _payload = {
                'attachments': [
                    {
                        "color": "#1fa3fb",
                        'blocks': [
                            {
                                'type': 'section',
                                'text': {
                                    'type': 'mrkdwn',
                                    'text': f'{message["recommended_by"]}さんのおすすめのイラストです!'
                                }
                            },
                            {
                                'type': 'header',
                                'text': {
                                    'type': 'plain_text',
                                    'text': f'{message["title"]}\n絵師様: {message["userName"]}',
                                    'emoji': True
                                }
                            },
                            {
                                'type': 'section',
                                'text': {
                                    'type': 'mrkdwn',
                                    'text': 'pixivで見る 👉'
                                },
                                'accessory': {
                                    'type': 'button',
                                    'text': {
                                        'type': 'plain_text',
                                        'text': 'Open pixiv',
                                        'emoji': True
                                    },
                                    'url': f'https://www.pixiv.net/artworks/{message["id"]}'
                                }
                            },
                            {
                                'type': 'section',
                                'text': {
                                    'type': 'plain_text',
                                    'text': 'Tags',
                                    'emoji': True
                                }
                            },
                            {
                                'type': 'section',
                                'fields': [
                                    {
                                        'type': 'plain_text',
                                        'text': message['tags'][0],
                                        'emoji': True
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            for i in range(1, 6) if len(message['tags']) > 6 else range(1, len(message['tags'])):
                _payload['attachments'][0]['blocks'][4]['fields'].append(
                    {
                        'type': 'plain_text',
                        'text': message['tags'][i],
                        'emoji': True
                    }
                )

            return json.dumps(_payload)
