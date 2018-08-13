from cleancat import ValidationError
from flask import request
from flask_restful import abort, Resource

from .helpers import get_db, request_json


DEFAULT_LIMIT = 100
DEFAULT_MAX_LIMIT = 100


class ModelBasedResource(Resource):
    def __init__(self):
        super(ModelBasedResource, self).__init__()
        self.sql = get_db()

    def get_model_class(self):
        return self.Meta.model

    def get_schema_class(self):
        return self.Meta.schema

    @property
    def raw_data(self):
        return request_json()

    def get_queryset(self):
        """Return the queryset that should be used for the current request.

        This method can return None instead of a queryset to indicate that
        the queryset is empty.
        """
        return self.get_model_class().query

    def get_object(self, pk):
        """
        Returns the object with the given pk. If get_queryset() has a filter,
        or if a custom PK field is used (e.g. with RandomPKMixin), an explicit
        pk_field must be specified in the resource's Meta class.
        """
        queryset = self.get_queryset()
        if queryset is None:
            return None

        pk_field = getattr(self.Meta, 'pk_field', None)
        if pk_field is not None:
            pk_field_instance = getattr(self.get_model_class(), pk_field)
            return queryset.filter(pk_field_instance == pk).one_or_none()
        else:
            return queryset.get(pk)

    def get_objects(self):
        queryset = self.get_queryset()
        if queryset is None:
            return [], False

        objs, has_more = self.paginate_query(queryset)
        return objs, has_more

    def save_object(self, obj):
        self.sql.session.add(obj)
        self.sql.session.commit()

    def get(self, pk=None):
        Schema = self.get_schema_class()

        if pk is None: # GET list
            objs, has_more = self.get_objects()
            data = [Schema(data=Schema.obj_to_dict(obj)).serialize()
                    for obj in objs]
            return {
                'data': data,
                'has_more': has_more,
            }, 200
        else: # GET single object
            obj = self.get_object(pk)
            if obj is None:
                abort(404)
            schema = Schema(data=Schema.obj_to_dict(obj))
            return schema.serialize(), 200

    def post(self):
        Schema = self.get_schema_class()
        schema = Schema(raw_data=self.raw_data)
        try:
            data = schema.full_clean()
        except ValidationError:
            abort(400, **{
                'field-errors': schema.field_errors,
                'errors': schema.errors,
            })

        obj = self.get_model_class()(**data)
        self.save_object(obj)

        schema = Schema(data=Schema.obj_to_dict(obj))
        return schema.serialize(), 201

    def put(self, pk):
        obj = self.get_object(pk)
        if obj is None:
            abort(404)

        Schema = self.get_schema_class()
        schema = Schema(raw_data=self.raw_data, data=Schema.obj_to_dict(obj))

        try:
            data = schema.full_clean()
        except ValidationError:
            abort(400, **{
                'field-errors': schema.field_errors,
                'errors': schema.errors,
            })

        dirty = False
        for key, value in data.items():
            if getattr(obj, key, None) != value:
                setattr(obj, key, value)
                dirty = True

        if dirty:
            self.save_object(obj)

        schema = Schema(data=Schema.obj_to_dict(obj))
        return schema.serialize(), 200

    def delete(self, pk):
        obj = self.get_object(pk)
        if obj is None:
            abort(404)

        self.delete_object(obj)
        return {}, 200

    def delete_object(self, obj):
        self.sql.session.delete(obj)
        self.sql.session.commit()

    def paginate_query(self, query):
        max_limit = getattr(self.Meta, 'max_limit', DEFAULT_MAX_LIMIT)

        given_limit = request.args.get('_limit')
        try:
            query_limit = int(given_limit)
        except (TypeError, ValueError):
            query_limit = None

        if query_limit is None:
            query_limit = getattr(self.Meta, 'limit', DEFAULT_LIMIT)

        if query_limit < 1:
            query_limit = 1
        elif query_limit > max_limit:
            query_limit = max_limit

        given_skip = request.args.get('_skip')
        try:
            query_skip = int(given_skip)
        except (TypeError, ValueError):
            query_skip = 0

        if query_skip < 0:
            query_skip = 0

        has_more = False

        query = query.offset(query_skip)
        query = query.limit(query_limit + 1)
        resp = query.all()

        if len(resp) == query_limit + 1:
            has_more = True
            resp = resp[:query_limit]

        return resp, has_more
