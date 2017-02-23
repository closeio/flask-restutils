# flask-restutils

Helpers for building REST APIs with Flask / SQLAlchemy / flask-restful.

## Management commands (`flask_restutils.commands`)

To use the management commands, you need both `flask-script` and `flask-sqlalchemy`. The provided commands are:

* `sqlcreate`: Creates all SQL tables
* `sqlreset`: Drops and recreates all SQL tables

All management can be added using the `add_sql_commands` helper as follows:

```
from flask_restutils.commands import add_sql_commands
add_sql_commands(manager)
```

## Helpers (`flask_restutils.helpers`)

* `get_db()`: Returns the SQLAlchemy database object. Requires `flask-sqlalchemy`.
* `request_json()`: Returns the (unserialized) JSON data from the request body, or raises a 400 error in case of an error or invalid content type. Requires Flask 0.11.

## Models (`flask_restutils.models`)

* `BaseModelMixin`: SQLAlchemy declarative model mixin that adds `date_created`/`date_updated` columns, a `Model.get()` method (shorthand for `Model.query.get(pk)`, and can be overridden in subclasses), and a nicer `__repr__`.
* `VersionMixin`: SQLAlchemy declarative model mixin that adds a version counter. It uses optimistic locking and raises `sqlalchemy.orm.exc.StaleDataError` when two concurrent transactions are trying to modify the model (see http://docs.sqlalchemy.org/en/latest/orm/versioning.html).

## Random PK (`flask_restutils.random_pk`)

Requires the `zbase62` module (https://github.com/closeio/zbase62/tree/python3-fixes).

Provides `RandomPKMixin`, a SQLAlchemy declarative model mixin that adds an `id` primary key column that internally uses a random UUID4, and publicly uses an ID comprised of a prefix and a Zbase62 representation of the UUID, e.g. `book_5ASpCqHpi5yyQRY0PjuUIR`. Example usage:

```
class Book(RandomPKMixin, sql.Model):
    __tablename__ = 'book'
```

The ID prefix by default consists of the first 4 letters of the model and can be customized as follows:

```
class Author(RandomPKMixin, sql.Model):
    __tablename__ = 'author'
    class Meta:
        id_prefix = 'author'
```

The UUID4 representation can be accessed through the `_id` field.

## Resources (`flask_restutils.resources`)

Requires `flask-restful` and `cleancat`.

Provides `ModelBasedResource`, a `flask_restful.Resource` subclass that provides CRUD functionality for SQLAlchemy models with cleancat schema validation.

Example resource:

```
from flask_restutils.resources import ModelBasedResource

from . import models, schemas

class BookResource(ModelBasedResource):
    class Meta:
        pk_field = 'id'
        model = models.Book
        schema = schemas.Book
```

Example schema:

```
class Book(Schema):
    id = String(read_only=True)
    author = String(mutable=False)
    title = String()
```

Example view:

```
from flask_restful import Api
from book.resources import BookResource

api = Api(app)
api.add_resource(BookResource, '/book/',
                               '/book/<pk>/')
```
