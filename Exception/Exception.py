
class Exception:

    default_exception = {'code': '1000', 'error': '', 'client_message': 'Whoops! You meet an error. Please refresh the page and try again. If still not working, please contact with Arthur.'}
    exceptions = [
        {'code': '1001', 'error': 'database is locked', 'client_message': 'Database is busy now, please wait for some seconds, refresh the page and try again.'}
    ]

    @classmethod
    def get_client_message(cls, e):
        for exception_ in cls.exceptions:
            if exception_['error'] == e:
                return exception_['client_message']
        return cls.default_exception['client_message']