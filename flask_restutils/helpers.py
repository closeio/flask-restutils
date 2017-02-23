from flask import current_app, request
from werkzeug.exceptions import BadRequest

def get_db(app=None):
    if not app:
        app = current_app
    return app.extensions['sqlalchemy'].db

def request_json():
    if not request.is_json:
        raise BadRequest({'errors': ['Invalid request: application/json expected.']})
    return request.get_json()
