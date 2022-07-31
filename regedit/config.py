import os
import json

from .errors import RegeditConfigInvalid
from http.cookies import SimpleCookie


class Config():
    def __init__(self):

        self.cookie = None
        self.interval = 60
        self.webhook_endpoints = {'discord': [], 'slack': []}
        self.users = None
    
    def load_config(self):
        cookie = SimpleCookie()
        cookie.load(os.getenv('COOKIE', ''))
        self.cookie = {key: value.value for key, value in cookie.items()}

        try:
            self.interval = int(os.getenv('INTERVAL', '60'))
        except ValueError:
            raise RegeditConfigInvalid('\"INTERVAL\" must be numeric')
        try:
            _endpoints = json.loads(os.getenv('WEBHOOKS',''))['webhooks']
            for url in _endpoints:
                if 'discord' in url:
                    self.webhook_endpoints['discord'].append(url)
                elif 'slack' in url:
                    self.webhook_endpoints['slack'].append(url)
                else:
                    raise RegeditConfigInvalid('Unknown webhook address type')
        except json.JSONDecodeError:
            raise RegeditConfigInvalid('\"WEBHOOKS\" has an invalid format')
        try:
            self.users = json.loads(os.getenv('USERS', ''))
        except json.JSONDecodeError:
            raise RegeditConfigInvalid('\"USERS\" has an invalid format')
    
        if not self.cookie:
            raise RegeditConfigInvalid('COOKIE is None')
        if int(self.interval) < 10:
            raise RegeditConfigInvalid('INTERVAL must be greater than or equal to 10')
        if not self.webhook_endpoints:
            raise RegeditConfigInvalid('No webhook endpoints specified')
        if not self.users:
            raise RegeditConfigInvalid('No user specified')
