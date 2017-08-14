import base64
import json

import iso8601
import jsonschema
from django.utils.encoding import force_bytes, force_text

from lepo.excs import ErroneousParameters, InvalidBodyContent, InvalidBodyFormat, MissingParameter
from lepo.utils import maybe_resolve

COLLECTION_FORMAT_SPLITTERS = {
    'csv': lambda value: force_text(value).split(','),
    'ssv': lambda value: force_text(value).split(' '),
    'tsv': lambda value: force_text(value).split('\t'),
    'pipes': lambda value: force_text(value).split('|'),
}

OPENAPI_JSONSCHEMA_VALIDATION_KEYS = (
    'maximum', 'exclusiveMaximum',
    'minimum', 'exclusiveMinimum',
    'maxLength', 'minLength',
    'pattern',
    'maxItems', 'minItems',
    'uniqueItems',
    'enum', 'multipleOf',
)


def cast_parameter_value(api_info, parameter, value):
    if parameter.get('type') == 'array':
        if not isinstance(value, list):  # could be a list already if collection format was multi
            splitter = COLLECTION_FORMAT_SPLITTERS.get(parameter.get('collectionFormat', 'csv'))
            if not splitter:
                raise NotImplementedError('unsupported collection format in %r' % parameter)
            value = splitter(value)
        items = parameter['items']
        value = [cast_parameter_value(api_info, items, item) for item in value]
    if 'schema' in parameter:
        schema = maybe_resolve(parameter['schema'], api_info.router.resolve_reference)
        jsonschema.validate(value, schema, resolver=api_info.router.resolver)
        if 'discriminator' in schema:  # Swagger Polymorphism support
            type = value[schema['discriminator']]
            actual_type = '#/definitions/%s' % type
            schema = api_info.router.resolve_reference(actual_type)
            jsonschema.validate(value, schema, resolver=api_info.router.resolver)
        return value
    value = cast_primitive_value(parameter, value)
    jsonschema_validation_object = {
        key: parameter[key]
        for key in parameter
        if key in OPENAPI_JSONSCHEMA_VALIDATION_KEYS
    }
    if jsonschema_validation_object:
        jsonschema.validate(value, jsonschema_validation_object)
    return value


def cast_primitive_value(spec, value):
    format = spec.get('format')
    type = spec.get('type')
    if type == 'boolean':
        return (force_text(value).lower() in ('1', 'yes', 'true'))
    if type == 'integer' or format in ('integer', 'long'):
        return int(value)
    if type == 'number' or format in ('float', 'double'):
        return float(value)
    if format == 'byte':  # base64 encoded characters
        return base64.b64decode(value)
    if format == 'binary':  # any sequence of octets
        return force_bytes(value)
    if format == 'date':  # ISO8601 date
        return iso8601.parse_date(value).date()
    if format == 'dateTime':  # ISO8601 datetime
        return iso8601.parse_date(value)
    if type == 'string':
        return force_text(value)
    return value


def read_body(request):
    consumes = request.api_info.operation.consumes
    if request.content_type not in consumes:
        raise InvalidBodyFormat('Content-type %s is not supported (%r are)' % (
            request.content_type,
            consumes,
        ))
    try:
        if request.content_type == 'application/json':
            return json.loads(request.body.decode(request.content_params.get('charset', 'UTF-8')))
        elif request.content_type == 'text/plain':
            return request.body.decode(request.content_params.get('charset', 'UTF-8'))
    except Exception as exc:
        raise InvalidBodyContent('Unable to parse this body as %s' % request.content_type) from exc
    raise NotImplementedError('No idea how to parse content-type %s' % request.content_type)  # pragma: no cover


def get_parameter_value(request, view_kwargs, param):
    if param['in'] == 'formData' and param.get('type') == 'file':
        return request.FILES[param['name']]

    if param['in'] in ('query', 'formData'):
        source = (request.POST if param['in'] == 'formData' else request.GET)
        if param.get('type') == 'array' and param.get('collectionFormat') == 'multi':
            return source.getlist(param['name'])
        else:
            return source[param['name']]

    if param['in'] == 'path':
        return view_kwargs[param['name']]

    if param['in'] == 'body':
        return read_body(request)

    if param['in'] == 'header':
        return request.META['HTTP_%s' % param['name'].upper().replace('-', '_')]

    raise NotImplementedError('unsupported `in` value in %r' % param)  # pragma: no cover


def read_parameters(request, view_kwargs):
    """
    :param request: HttpRequest with attached api_info
    :type request: HttpRequest
    :type view_kwargs: dict[str, object]
    :rtype: dict[str, object]
    """
    params = {}
    errors = {}
    for param in request.api_info.operation.parameters:
        try:
            value = get_parameter_value(request, view_kwargs, param)
        except KeyError:
            if 'default' in param:
                params[param['name']] = param['default']
                continue
            if param.get('required'):  # Required but missing
                errors[param['name']] = MissingParameter('parameter %s is required but missing' % param['name'])
            continue
        try:
            params[param['name']] = cast_parameter_value(request.api_info, param, value)
        except NotImplementedError:
            raise
        except Exception as e:
            errors[param['name']] = e
    if errors:
        raise ErroneousParameters(errors, params)
    return params
