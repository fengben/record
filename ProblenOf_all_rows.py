import tablib
from collections import OrderedDict
from inspect import isclass
from sqlalchemy import create_engine,text


def _reduce_datetimes(row):
    """Receives a row, converts datetimes to strings."""

    row = list(row)

    for i in range(len(row)):
        if hasattr(row[i], 'isoformat'):
            row[i] = row[i].isoformat()
    return tuple(row)



class Record(object):
    __slots__ = ('_keys', '_values')
    def __init__(self,keys,values):
        self._keys=keys
        self._values=values
        assert len(self._keys)==len(self._values)

    def as_dict(self):
        '''merge keys(list) values(list) into a dict(['keys':values])'''
        dict(zip(self._keys,self._values))
        return dict
    def keys(self):
        return self._keys

    def values(self):
        return self._values

    def get(self,key):
        return  self.as_dict()[key]

    def __repr__(self):
        return '<Record {}>'.format(self.export('json')[1:-1])

    @property
    def dataset(self):
        """A Tablib Dataset containing the row."""
        data = tablib.Dataset()
        data.headers = self.keys()

        row = _reduce_datetimes(self.values())
        data.append(row)

        return data

    def export(self, format, **kwargs):
        """Exports the row to the given format."""
        return self.dataset.export(format, **kwargs)
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __dir__(self):
        standard = dir(super(Record, self))
        # Merge standard attrs with generated ones (from column names).
        return sorted(standard + [str(k) for k in self.keys()])

    def __getitem__(self, key):
        # Support for index-based lookup.
        if isinstance(key, int):
            return self.values()[key]

        # Support for string-based lookup.
        if key in self.keys():
            i = self.keys().index(key)
            return self.values()[i]

        raise KeyError("Record contains no '{}' field.".format(key))

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)


class Database(object):
    def __init__(self, url, **kwargs):
        # create engine
        self._engine = create_engine(url, **kwargs)
        self.connect = self._engine.connect()
        self.open = True
    def query(self,query,**kwargs):
        cursor=self.connect.execute(text(query),params)
        print('debug begin')
        row_gen=(Record(cursor.keys(),rows) for rows in cursor)

        # i=0
        # aaa=[]
        # if i<len(row_gen):
        #     aaa[i]=yield row_gen[i]
        results=RecordCollection(row_gen)
        return results


class RecordCollection(object):
    """A set of excellent Records fr om a query."""
    def __init__(self, rows):
        self._rows = rows
        print(type(self._rows))
        self._all_rows = []
        self.pending = True
        print('__init__ executed')

    def __repr__(self):
        return '<RecordCollection size={} pending={}>'.format(len(self), self.pending)

    def __iter__(self):
        """Iterate over all rows, consuming the underlying generator
        only when necessary."""
        i = 0
        print('__iter__ executed')
        while True:
            # Other code may have iterated between yields,
            # so always check the cache.
            if i < len(self):
                print(type(self[i]))
                yield self[i]
            else:
                # Throws StopIteration when done.
                # Prevent StopIteration bubbling from generator, following https://www.python.org/dev/peps/pep-0479/
                try:
                    yield next(self)
                except StopIteration:
                    return
            i += 1

    def next(self):
        print('next executed')
        return self.__next__()

    def __next__(self):
        print('__next__ executed')
        try:
            nextrow = next(self._rows)
            self._all_rows.append(nextrow)
            return nextrow
        except StopIteration:
            self.pending = False
            raise StopIteration('RecordCollection contains no more rows.')

    def __len__(self):
        print('__len__ executed')
        return len(self._all_rows)



    @property
    def dataset(self):
        """A Tablib Dataset representation of the RecordCollection."""
        # Create a new Tablib Dataset.
        print('dataset executed')
        data = tablib.Dataset()

        # If the RecordCollection is empty, just return the empty set
        # Check number of rows by typecasting to list
        if len(list(self)) == 0:
            return data

        # Set the column names as headers on Tablib Dataset.
        first = self[0]

        data.headers = first.keys()
        for row in self.all():
            row = _reduce_datetimes(row.values())
            data.append(row)

        return data



if __name__=='__main__':
    url = 'mysql+mysqldb://feng:f1234@localhost/blog?charset=utf8'
    db = Database(url)
    query = 'select * from blog_post where status=:status'
    params = {'status': 'draft'}
    result = db.query(query, **params)
    print(result)