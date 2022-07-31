import os

from .errors import RegeditConfigInvalid
from http.cookies import SimpleCookie


class Config():
    def __init__(self):

        cookie = SimpleCookie()
        cookie.load(os.getenv('COOKIE', ''))
        self.cookie = {key: value.value for key, value in cookie.items()}
        try:
            self.interval = int(os.getenv('INTERVAL', '60'))
        except ValueError:
            raise RegeditConfigInvalid('\"INTERVAL\" must be numeric')
        self.slack_endpoint = os.getenv('SLACK_ENDPOINT','')
        self.discord_endpoint = os.getenv('DISCORD_ENDPOINT', '')
        self.user = os.getenv('USER', '')
        try:
            self.id = int(os.getenv('ID'))
        except ValueError:
            raise RegeditConfigInvalid('\"ID\" must be numeric')
    
    def valid_config(self):
        if not self.cookie:
            raise RegeditConfigInvalid('COOKIE is not defined')
        if int(self.interval) < 10:
            raise RegeditConfigInvalid('INTERVAL must be greater than or equal to 10')
        if not self.slack_endpoint and not self.discord_endpoint:
            raise RegeditConfigInvalid('No endpoint specified')

        if self.user == None:
            raise RegeditConfigInvalid('No user specified')
        if self.id == None:
            raise RegeditConfigInvalid('No id specified')
