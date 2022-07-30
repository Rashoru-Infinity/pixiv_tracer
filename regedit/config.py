import json
from pathlib import Path

from .errors import RegeditConfigInvalid


class Config():
    def __init__(self, config_file_path='config.json'):
        self.config_path = Path(config_file_path)

        self.cookie = {}
        self.interval = 60
        self.webhook_endpoints = {'discord': [], 'slack': []}
        self.users = []

    def load_config(self):
        _config = {}
        with open(self.config_path, 'r') as _f:
            try:
                _config = json.load(_f)
            except json.JSONDecodeError:
                raise RegeditConfigInvalid('Invalid format. Accept only JSON')
            except Exception as _e:
                raise _e

        self.cookie = _config.get('cookie')
        if not self.cookie:
            raise RegeditConfigInvalid('Cookie is None')
        self.cookie['login_ever'] = 'yes'

        self.interval = _config.get('interval') or 60

        _endpoints = _config.get('webhook_endpoints')
        if not _endpoints:
            raise RegeditConfigInvalid('Webhook endpoint is not set')

        for url in _endpoints:
            if 'discord' in url:
                self.webhook_endpoints['discord'].append(url)
            elif 'slack' in url:
                self.webhook_endpoints['slack'].append(url)
            else:
                raise RegeditConfigInvalid('Unknown webhook address type')

        self.users = _config.get('users')
        if not self.users:
            raise RegeditConfigInvalid('Users is None')
