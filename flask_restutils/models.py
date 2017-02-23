import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr


class BaseModelMixin(object):
    @classmethod
    def get(cls, pk):
        return cls.query.get(pk)

    @declared_attr
    def date_created(cls):
        return Column(DateTime, default=datetime.datetime.utcnow)

    @declared_attr
    def date_updated(cls):
        return Column(DateTime, default=datetime.datetime.utcnow,
                      onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        if getattr(self, 'id', None):
            return "<%s: %s>" % (self.__class__.__name__, self.id)
        return "<%s instance>" % (self.__class__.__name__)


class VersionMixin(object):
    version_id = Column(Integer, nullable=False)

    __mapper_args__ = {
        'version_id_col': version_id,
    }
