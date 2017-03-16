from flask import current_app, request
from functools import wraps
from werkzeug.exceptions import BadRequest

def get_db(app=None):
    if not app:
        app = current_app
    return app.extensions['sqlalchemy'].db

def request_json():
    if not request.is_json:
        raise BadRequest({'errors': ['Invalid request: application/json expected.']})
    return request.get_json()

def rollback_on_error(session):
    """
    Function that returns a decorator that rolls back the given session if an
    exception occurrs.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                session.rollback()
                raise
        return wrapped
    return decorator
