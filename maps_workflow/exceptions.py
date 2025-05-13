import json


class RuleError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RuleViolationError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors

    def __json__(self):
        return json.dumps({})
