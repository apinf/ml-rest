from lepo.excs import RouterValidationError


def validate_router(router):
    errors = {}
    operations = set()
    for path in router.get_paths():
        for operation in path.get_operations():
            operations.add(operation.id)
    for operation in operations:
        try:
            router.get_handler(operation)
        except Exception as e:
            errors[operation] = e
    if errors:
        raise RouterValidationError(errors)
