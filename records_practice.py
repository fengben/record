from sqlalchemy import create_engine,text
import tablib


#connect db
class Database(object):
    def __init__(self,url,**kwargs):
        #create engine
        self._engine=create_engine(url,**kwargs)
        self.connect=self._engine.connect()
        self.open=True

    def close(self):
        self.connect.close()
        self.open=False

    def query(self,query,*args,**kwargs):
        cursor=self.connect.execute(text(query),params)
        # for rows in cursor:
        #     Record(rows.keys(),rows.values())
        # for row in cursor:
        #     #print(row.keys())
        #     assert row==row.values()
        row_gen=(Record(cursor.keys(),rows) for rows in cursor)
        # for i in row_gen:
        #     print(i.as_dict())
        #     print('/n')
        #print(next(row_gen).values())
        # i=next(row_gen)
        # print(i)
        results=RecordCollection(row_gen)
        return results

    def all(self, as_dict=False, as_ordereddict=False):
        """Returns a list of all rows for the RecordCollection. If they haven't
        been fetched yet, consume the iterator and cache the results."""

        # By calling list it calls the __iter__ method
        rows = list(self)

        if as_dict:
            return [r.as_dict() for r in rows]
        elif as_ordereddict:
            return [r.as_dict(ordered=True) for r in rows]

        return rows

    def as_dict(self, ordered=False):
        return self.all(as_dict=not(ordered), as_ordereddict=ordered)

    def first(self, default=None, as_dict=False, as_ordereddict=False):
        """Returns a single record for the RecordCollection, or `default`. If
        `default` is an instance or subclass of Exception, then raise it
        instead of returning it."""

        # Try to get a record, or return/raise default.
        try:
            record = self[0]
        except IndexError:
            # if isexception(default):
            #     raise default
            return default

        # Ensure that we don't have more than one row.
        try:
            self[1]
        except IndexError:
            pass
        else:
            raise ValueError('RecordCollection contains too many rows.')

        # Cast and return.
        if as_dict:
            return record.as_dict()
        elif as_ordereddict:
            return record.as_dict(ordered=True)
        else:
            return record
    def __getitem__(self, key):
        is_int = isinstance(key, int)

        # Convert RecordCollection[1] into slice.
        if is_int:
            key = slice(key, key + 1)

        while len(self) < key.stop or key.stop is None:
            try:
                next(self)
            except StopIteration:
                break

        rows = self._all_rows[key]
        if is_int:
            return rows[0]
        else:
            return RecordCollection(iter(rows))

    def __len__(self):
        return len(self._all_rows)

    def export(self, format, **kwargs):
        """Export the RecordCollection to a given format (courtesy of Tablib)."""
        return self.dataset.export(format, **kwargs)

class RecordCollection(object):
    def __init__(self,rows):
        self._rows=rows
        self._all_rows= []
        self.pending=True

    def __iter__(self):
        i=0
        while (True):
            if i<len(self):
                yield self[i]
            else:
                try:
                    yield next(self)
                except StopIteration:
                    return
            i+=1

    def next(self):
        return self.__next__()

    def __next__(self):
        try:
            nextrow=next(self._rows)
            self._all_rows.append(nextrow)
            return nextrow
        except StopIteration:
            raise StopIteration('no more rows')

    def __len__(self):
        return len(self._all_rows)

    @property
    def dataset(self):
        """A Tablib Dataset representation of the RecordCollection."""
        # Create a new Tablib Dataset.
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

def _reduce_datetimes(row):
    """Receives a row, converts datetimes to strings."""

    row = list(row)

    for i in range(len(row)):
        if hasattr(row[i], 'isoformat'):
            row[i] = row[i].isoformat()
    return tuple(row)


if __name__=='__main__':
    url='mysql+mysqldb://feng:f1234@localhost/blog?charset=utf8'
    db=Database(url)
    query='select * from blog_post where status=:status'
    params={'status':'draft'}
    result=db.query(query,**params)
    print(result)