from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest
from sqlalchemy import Column, Integer
from sqlalchemy.orm.exc import StaleDataError

from flask_restutils.models import VersionMixin


TEST_DB_URL = 'sqlite:///tmp/test_restutils.db'


class TestRestutils:
    def setup_method(self, test_method):
        app = Flask('test_app')
        app.config['SQLALCHEMY_DATABASE_URL'] = TEST_DB_URL
        self.sql = SQLAlchemy(app)

    def test_version_mixin(self):
        sql = self.sql

        class VersionTest(sql.Model, VersionMixin):
            __tablename__ = 'version_test'
            id = Column(Integer, primary_key=True)
            value = Column(Integer)

        sql.create_all()

        v = VersionTest(value=1)
        sql.session.add(v)
        sql.session.commit()

        other_session = sql.create_scoped_session()

        v.value = 3

        v2 = other_session.query(VersionTest).get(v.id)
        v2.value = 2

        assert other_session.is_active

        sql.session.commit()
        pytest.raises(StaleDataError, other_session.commit)

        assert v.value == 3
        assert v.version_id == 2

        if not other_session.is_active:
            other_session.rollback()
        v2 = other_session.query(VersionTest).get(v.id)
        v2.value = 2
        sql.session.commit()
