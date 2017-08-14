from copy import deepcopy
from functools import wraps

from django.utils.module_loading import import_string


class BaseHandler:
    def __init__(self, request, args):
        self.request = request
        self.args = args

    @classmethod
    def get_view(cls, method_name):
        """
        Get a Django function view calling the given method (and pre/post-processors)

        :param method_name: The method on the class
        :return: View function
        """
        method = getattr(cls, method_name)

        @wraps(method)
        def view(request, **kwargs):
            handler = cls(request, kwargs)
            handler.call_processors('view')
            response = None
            try:
                response = method(handler)
                return response
            finally:
                handler.call_processors('post_view', response=response)

        return view

    def get_processors(self, purpose):
        return getattr(self, '%s_processors' % purpose, ())

    def call_processors(self, purpose, **kwargs):
        for proc in self.get_processors(purpose):
            if isinstance(proc, str):
                proc = getattr(self, proc, None) or import_string(proc)
            kwargs['purpose'] = purpose
            proc(**kwargs)


class BaseModelHandler(BaseHandler):
    model = None
    queryset = None
    schema_class = None

    id_data_name = 'id'
    id_field_name = 'pk'

    def get_schema(self, purpose, object=None):
        schema_class = getattr(self, '%s_schema_class' % purpose, None)
        if schema_class is None:
            schema_class = self.schema_class
        kwargs = {}
        if purpose == 'update':
            kwargs['partial'] = True
        return schema_class(**kwargs)

    def get_queryset(self, purpose):
        queryset = getattr(self, '%s_queryset' % purpose, None)
        if queryset is None:
            queryset = self.queryset
        return deepcopy(queryset)

    def process_object_list(self, purpose, object_list):
        return object_list

    def retrieve_object(self):
        queryset = self.get_queryset('retrieve')
        object = queryset.get(**{self.id_field_name: self.args[self.id_data_name]})
        self.call_processors('retrieve_object', object=object)
        return object


class ModelHandlerReadMixin(BaseModelHandler):
    def handle_list(self):
        self.call_processors('list')
        queryset = self.get_queryset('list')
        object_list = self.process_object_list('list', queryset)
        schema = self.get_schema('list')
        return schema.dump(object_list, many=True).data

    def handle_retrieve(self):
        self.call_processors('retrieve')
        object = self.retrieve_object()
        schema = self.get_schema('retrieve')
        return schema.dump(object).data


class ModelHandlerCreateMixin(BaseModelHandler):
    create_data_name = 'data'

    def handle_create(self):
        self.call_processors('create')
        schema = self.get_schema('create')
        result = schema.load(self.args[self.create_data_name])
        assert not result.errors
        data = result.data
        if not isinstance(data, self.model):
            data = self.model(**data)

        data.full_clean()
        data.save()

        schema = self.get_schema('post_create', object=data)
        return schema.dump(data).data


class ModelHandlerUpdateMixin(BaseModelHandler):
    update_data_name = 'data'

    def handle_update(self):
        self.call_processors('update')
        object = self.retrieve_object()
        schema = self.get_schema('update', object=object)
        result = schema.load(self.args[self.update_data_name])
        assert not result.errors
        for key, value in result.data.items():
            setattr(object, key, value)
        object.full_clean()
        object.save()
        self.call_processors('post_update', object=object)
        schema = self.get_schema('post_update', object=object)
        return schema.dump(object).data


class ModelHandlerDeleteMixin(BaseModelHandler):
    def handle_delete(self):
        self.call_processors('delete')
        object = self.retrieve_object()
        object.delete()
        self.call_processors('post_delete', object=object)


class CRUDModelHandler(
    ModelHandlerCreateMixin,
    ModelHandlerReadMixin,
    ModelHandlerUpdateMixin,
    ModelHandlerDeleteMixin,
):
    pass
