class ODPException(Exception):
    def __init__(self, *args, **kwargs):
        self.status_code = kwargs.pop('status_code', None)
        self.error_detail = kwargs.pop('error_detail', str(args))


class ODPClientError(ODPException):
    pass


class ODPServerError(ODPException):
    pass


class ODPAuthError(ODPException):
    pass
