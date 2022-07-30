import json
from pathlib import Path

from .errors import RegeditConfigInvalid


class Config():
    def __init__(self, config_file_path='config.json'):
        self.config_path = Path(config_file_path)

        self.cookie = {}
        self.cache_dir = None
        self.interval = 60
        self.webhook_endpoint = ''
        self.webhook_type = ''
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

        self.cache_dir = Path(_config['img_dir']) \
            if 'img_dir' in _config else Path('cache')

        self.interval = _config.get('interval') or 60

        self.webhook_endpoint = _config.get('webhook_endpoint')
        if not self.webhook_endpoint:
            raise RegeditConfigInvalid('Webhook endpoint is not set')

        if 'discord' in self.webhook_endpoint:
            self.webhook_type = 'discord'
        elif 'slack' in self.webhook_endpoint:
            self.webhook_type = 'slack'
        else:
            raise RegeditConfigInvalid('Unknown webhook address type')

        self.users = _config.get('users')
        if not self.users:
            raise RegeditConfigInvalid('Users is None')
