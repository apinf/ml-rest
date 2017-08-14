from django.utils.text import camel_case_to_spaces


def maybe_resolve(object, resolve):
    """
    Call `resolve` on the `object`'s `$ref` value if it has one.

    :param object: An object.
    :param resolve: A resolving function.
    :return: An object, or some other object! :sparkles:
    """
    if isinstance(object, dict) and object.get('$ref'):
        return resolve(object['$ref'])
    return object


def snake_case(string):
    return camel_case_to_spaces(string).replace(' ', '_')
