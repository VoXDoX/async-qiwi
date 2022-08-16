
class ApiError(Exception):
    pass


class WrongToken(ApiError):
    pass


class PermError(ApiError):
    pass
