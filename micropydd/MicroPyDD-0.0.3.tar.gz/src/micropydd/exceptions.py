class PyddException(Exception):

    def __init__(self, message) -> None:
        super().__init__(message)
        self.message = message


class LevelNameNotFoundException(PyddException):

    def __init__(self, level_name):
        super().__init__(f'Level name not found [{level_name}]')


class LevelNotSetException(PyddException):

    def __init__(self, level_name):
        super().__init__(f'Level cannot be set for [{level_name}]')


class MethodNotImplementedException(PyddException):
    pass


class EnvironmentVariableNotFound(PyddException):

    def __init__(self, var) -> None:
        super().__init__(f'Var not found {var}')
        self.var = var


class ConfigurationNotFound(PyddException):

    def __init__(self, conf) -> None:
        self.conf = conf
