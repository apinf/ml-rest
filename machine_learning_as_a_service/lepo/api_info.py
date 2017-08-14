class APIInfo:
    def __init__(self, operation):
        """
        :type operation: lepo.operation.Operation
        """
        self.router = operation.router
        self.path = operation.path
        self.operation = operation
