import tablib
import os
from sqlalchemy import create_engine, inspect, text
from collections import OrderedDict
from inspect import isclass
from docopt import docopt

DATABASE_URL = os.environ.get('DATABASE_URL')

class Database(object):
    """A Database connection."""

    def __init__(self, db_url=None, **kwargs):
        # If no db_url was provided, fallback to $DATABASE_URL.
        self.db_url = db_url or DATABASE_URL

        if not self.db_url:
            raise ValueError('You must provide a db_url.')

        self._engine = create_engine(self.db_url, **kwargs)

        # Connect to the database.
        self.db = self._engine.connect()
        self.open = True

    def close(self):
        """Closes the connection to the Database."""
        self.db.close()
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def __repr__(self):
        return '<Database open={}>'.format(self.open)

    def get_table_names(self, internal=False):
        """Returns a list of table names for the connected database."""

        # Setup SQLAlchemy for Database inspection.
        return inspect(self._engine).get_table_names()

    def query(self, query, fetchall=False, **params):
        """Executes the given SQL query against the Database. Parameters
        can, optionally, be provided. Returns a RecordCollection, which can be
        iterated over to get result rows as dictionaries.
        """

        # Execute the given query.
        cursor = self.db.execute(text(query), **params) # TODO: PARAMS GO HERE

        # Row-by-row Record generator.
        row_gen = (Record(cursor.keys(), row) for row in cursor)

        # Convert psycopg2 results to RecordCollection.
        results = RecordCollection(row_gen)

        # Fetch all results if desired.
        if fetchall:
            results.all()

        return results

    def query_file(self, path, fetchall=False, **params):
        """Like Database.query, but takes a filename to load a query from."""

        # If path doesn't exists
        if not os.path.exists(path):
            raise IOError("File '{}'' not found!".format(path))

        # If it's a directory
        if os.path.isdir(path):
            raise IOError("'{}' is a directory!".format(path))

        # Read the given .sql file into memory.
        with open(path) as f:
            query = f.read()

        # Defer processing to self.query method.
        return self.query(query=query, fetchall=fetchall, **params)

    def transaction(self):
        """Returns a transaction object. Call ``commit`` or ``rollback``
        on the returned object as appropriate."""
        return self.db.begin()

if __name__ == '__main__':
    #db = Database(arguments['--url'])
    dict={'USER':'feng'}
    DB_CONNECT_STRING = 'mysql+mysqldb://feng:f1234@localhost/blog?charset=utf8'
    db=Database(DB_CONNECT_STRING)
    #print(DATABASE_URL)    value=None