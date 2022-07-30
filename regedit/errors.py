class RegeditFucked(Exception):
    def __str__(self) -> str:
        return 'regedit fucked'


class RegeditConfigInvalid(RegeditFucked):
    def __init__(self, message):
        self.message = message

    def __str__(self) -> str:
        return f'Config file is invalid: {self.message}'
