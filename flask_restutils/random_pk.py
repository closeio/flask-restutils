import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import TypeDecorator
from zbase62 import zbase62


def uuid_to_id(uuid_obj, prefix):
    return '{}_{}'.format(prefix, zbase62.b2a(uuid_obj.bytes))


def id_to_uuid(id_str):
    uuid_bytes = zbase62.a2b(str(id_str[id_str.find('_') + 1:]))
    return uuid.UUID(bytes=uuid_bytes)


class RandomPKField(TypeDecorator):
    impl = UUID(as_uuid=True)
    python_type = str

    def __init__(self, prefix, *args, **kwargs):
        self.prefix = prefix
        super(RandomPKField, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        try:
            return id_to_uuid(value) if value else None
        except ValueError:
            return None

    def process_result_value(self, value, dialect):
        return uuid_to_id(value, self.prefix) if value else None


class RandomPKMixin(object):
    @declared_attr
    def id(cls):
        prefix = cls.get_id_prefix()
        return Column(
            'id',
            RandomPKField(prefix),
            default=cls.generate_id,
            primary_key=True
        )

    @classmethod
    def generate_id(cls):
        return uuid_to_id(uuid.uuid4(), cls.get_id_prefix())

    @classmethod
    def get_id_prefix(cls):
        if hasattr(cls, 'Meta') and hasattr(cls.Meta, 'id_prefix'):
            return cls.Meta.id_prefix

        # Generate prefix based on table name
        id_prefix = cls.__tablename__[:4]
        for i in range(0, 4 - len(id_prefix)):
            id_prefix += '_'
        return id_prefix

    @property
    def pk(self):
        return self.id
