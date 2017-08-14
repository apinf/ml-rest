class MissingParameter(ValueError):
    pass


class InvalidOperation(ValueError):
    pass


class MissingHandler(ValueError):
    pass


class ErroneousParameters(Exception):
    def __init__(self, error_map, parameters):
        self.errors = error_map
        self.parameters = parameters


class InvalidBodyFormat(ValueError):
    pass


class InvalidBodyContent(ValueError):
    pass


class RouterValidationError(Exception):
    def __init__(self, error_map):
        self.errors = error_map
        self.description = '\n'.join('%s: %s' % (key, value) for (key, value) in sorted(self.errors.items()))
        super(RouterValidationError, self).__init__('Router validation failed:\n%s' % self.description)


class ExceptionalResponse(Exception):
    """
    Wraps a Response in an exception.

    These exceptions are caught in PathView.
    """
    def __init__(self, response):
        self.response = response
