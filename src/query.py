

class Query():
    """Holds a database query string. Used to reuse a single filtered query for
    different operations that require different data or information. The
    query methods only work while the database is still open.
    """

    def __init__(self, database, model, filters=None, params=None):
        """(Query, Database, Model, [str], list) -> None
        Constructs a query using the given parameters.
        """
        self.database = database
        self.params = params
        self.model = model
        self.params = tuple(params)

        # If the filter list is non-empty, format it into an SQL query.
        if filters:
            self.query = 'WHERE ' + 'AND '.join(filters)
        else:
            self.query = ''

    def all(self, by='', asc=True):
        """(Query, str, Bool) -> [dict]
        Returns all the objects in the database that match the given query,
        as dictionaries
        """
        # Get the rows from the database.
        return self.database.query(
            self.model,
            'SELECT %s FROM %s %s %s' %
            (self.model.db_labels,
             self.model.db_from,
             self.query,
             self._order(by, asc)),
            self.params)

    def count(self):
        """(Query) -> int
        Returns the number of rows in the query.
        """
        # Try running the query on the given paramaters. The returned value
        # needs to be a dictionary, since most classes won't have a member
        # to store the count (and shouldn't be modified to support that...)
        result = self.database.query(
            self.model,
            'SELECT count(*) as c FROM %s %s' %
            (self.model.db_table, self.query),
            self.params,
            convert=False)

        if result:
            return result[0]['c']
        else:
            # Invalid queries produce no results.
            return 0

    def first(self):
        """(Query) -> dict
        Returns the dictionary for the first object in the database that
        matches the Query, or None if there were no objects that matched the
        filters in the query.
        """
        rows = self.subset(0, 1)
        if rows:
            return rows[0]
        else:
            return None

    def _order(self, by='', asc=True):
        """(Query, str, Bool) -> str
        Private function that returns the order string, ordering by a given
        field, and either ascending or descending. Returns the empty string
        if no by ordering was given.
        """
        if by:
            # Determine the direction to order by
            dir = 'ASC' if asc else 'DESC'

            # Ordering given. Return the SQL order expression.
            return 'ORDER BY %s %s' % (by, dir)
        else:
            # No ordering given, return the empty string.
            return ''

    def subset(self, offset=0, length=10, by='', asc=True):
        """(Query, int, int, str, Bool) -> [dict]
        Returns a subset of all the objects in the database that match the
        given query, as dictionaries.
        """
        return self.database.query(
            self.model,
            'SELECT %s FROM %s %s %s LIMIT %d OFFSET %d' %
            (self.model.db_labels,
             self.model.db_from,
             self.query,
             self._order(by, asc),
             length,
             offset),
            self.params)