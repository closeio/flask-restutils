from __future__ import print_function

from .helpers import get_db


__all__ = ['add_sql_commands']


try:
    input = raw_input # Python 2
except NameError:
    pass


def sqlcreate():
    """Creates all SQL tables."""
    sql = get_db()
    sql.create_all()

def sqlreset():
    """Drops and recreates all SQL tables."""
    sql = get_db()
    print('This will drop and recreate all SQL tables. Are you sure? [y] ', end='')
    if input() == 'y':
        sql.drop_all()
        sql.create_all()
    else:
        print('Aborted.')

def add_sql_commands(manager):
    """
    Adds the "sqlcreate" and "sqlreset" commands to a flask-script manager. The
    SQL instance can be passed directly or lazily (as a callable).
    """
    from flask_script import Command
    manager.add_command('sqlcreate', Command(sqlcreate))
    manager.add_command('sqlreset', Command(sqlreset))
