from collections import OrderedDict

from django.utils.functional import cached_property

from lepo.utils import maybe_resolve


class Operation:
    def __init__(self, router, path, method, data):
        """
        :type router: lepo.router.Router
        :type path: lepo.path.Path
        :type method: str
        :type data: dict
        """
        self.router = router
        self.path = path
        self.method = method
        self.data = data

    @property
    def id(self):
        return self.data['operationId']

    @cached_property
    def parameters(self):
        """
        Combined path-level and operation-level parameters.

        Any $refs are resolved here.

        Note that this implementation differs from the spec in that we only use
        the _name_ of a parameter to consider its uniqueness, not the name and location.

        This is because we end up passing parameters to the handler by name anyway,
        so any duplicate names, even if they had different locations, would be horribly mangled.

        :rtype: list[dict]
        """

        parameters = OrderedDict()
        for source in (
            self.path.mapping.get('parameters', ()),
            self.data.get('parameters', {}),
        ):
            source = maybe_resolve(source, self.router.resolve_reference)
            for parameter in source:
                parameter = maybe_resolve(parameter, self.router.resolve_reference)
                parameters[parameter['name']] = parameter

        return list(parameters.values())

    def _get_overridable(self, key, default=None):
        # TODO: This probes a little too deeply into the specifics of these objects, I think...
        for obj in (
            self.data,
            self.path.mapping,
            self.router.api,
        ):
            if key in obj:
                return obj[key]
        return default

    @cached_property
    def consumes(self):
        value = self._get_overridable('consumes', [])
        if not isinstance(value, (list, tuple)):
            raise TypeError('`consumes` must be a list, got %r' % value)  # pragma: no cover
        return value

    @cached_property
    def produces(self):
        value = self._get_overridable('produces', [])
        if not isinstance(value, (list, tuple)):
            raise TypeError('`produces` must be a list, got %r' % value)  # pragma: no cover
        return value
