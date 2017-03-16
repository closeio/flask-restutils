import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import synonym
from sqlalchemy.orm.properties import ColumnProperty
from zbase62 import zbase62


def uuid_to_id(uuid_obj, prefix):
    return '{}_{}'.format(prefix, zbase62.b2a(uuid_obj.bytes))


def id_to_uuid(id_str):
    uuid_bytes = zbase62.a2b(str(id_str[id_str.find('_') + 1:]))
    return uuid.UUID(bytes=uuid_bytes)


class RandomPKComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        try:
            uuid_str = str(id_to_uuid(other))
        except ValueError:
            return False
        return self.__clause_element__() == uuid_str


def RandomPK(id_field):
    def getter(self):
        value = getattr(self, id_field)
        if value:
            return uuid_to_id(uuid.UUID(value), self.get_id_prefix())

    def attr(cls):
        return synonym(id_field,
                       descriptor=property(getter),
                       comparator_factory=RandomPKComparator)

    return declared_attr(attr)


class RandomPKMixin(object):
    _id = Column('id', UUID, default=lambda: str(uuid.uuid4()),
                 primary_key=True)
    id = RandomPK('_id')

    @classmethod
    def get(cls, pk):
        try:
            internal_pk = cls.to_internal_pk(pk)
        except ValueError:
            return
        return cls.query.get(internal_pk)

    @classmethod
    def to_internal_pk(cls, pk):
        """
        Maps a public ID value to the internal primary key.
        Raises ValueError if an incorrect value is given.
        """
        return str(id_to_uuid(pk))

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
