import sqlite3
from query import Query
from source import Source
from article import Article
from reference import Reference
from keywords import Keyword
from watch import Watch


class Database():
    """The database class handles a connection to a database. The database
    works with objects, and returns objects. The objects that the database
    works with must be derived from Model, so the database understands
    how the object relates to its tables.

    For adding, modifying, and deleting data, it is sufficient to call the
    appropriate functions in the database that match the given object.

    For getting data from the database, get_by_id returns the object itself,
    while queries that rely on filtered data from the database will return
    a Query object - which can be used to get multiple objects from the
    database, or the count of the objects that matched the query.
    """

    def __init__(self, path):
        """(Database, str) -> None
        Creates a connection to the database for the given path.
        """
        # Create the connection, and get the SQLite3 connection cursor.
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

        # Enable foreign key support, since it is not on by default in SQLite3.
        self.cursor.execute("PRAGMA foreign_keys = ON")

        # Rows are normally returned as tuples, but by using a custom
        # function, they can be returned as dicts.
        self.cursor.row_factory = row_to_dict

    def close(self):
        """(Database) -> None
        Closes the connection to the current database.
        """
        if self.connection:
            self.connection.close()

    def create_tables(self):
        """(Database) -> None
        Creates the tables for the database. If the tables already exist,
        then nothing is changed.
        """
        try:
            # Create the sources table.
            self.execute(
                "CREATE TABLE source("
                "id INTEGER PRIMARY KEY NOT NULL, "
                "url TEXT UNIQUE NOT NULL)")

            # Create the keywords table.
            self.execute(
                "CREATE TABLE keyword( "
                "id INTEGER PRIMARY KEY, "
                "source_id INTEGER, "
                "name TEXT UNIQUE NOT NULL, "
                "FOREIGN KEY(source_id) REFERENCES source(id) ON DELETE "
                "CASCADE)")

            # Create the articles table.
            self.execute(
                "CREATE TABLE article("
                "id INTEGER PRIMARY KEY NOT NULL, "
                "source_id INTEGER NOT NULL, "
                "url TEXT UNIQUE NOT NULL, "
                "title TEXT NOT NULL, "
                "date DATE NOT NULL, "
                "author TEXT NOT NULL, "
                "tags TEXT NOT NULL, "
                "FOREIGN KEY(source_id) REFERENCES source(id) ON DELETE "
                "CASCADE)")

            # Create the watchlist table.
            self.execute(
                "CREATE TABLE watch("
                "id INTEGER PRIMARY KEY NOT NULL, "
                "url TEXT UNIQUE NOT NULL,"
                "domain TEXT UNIQUE NOT NULL)")

            # Create the reference table.
            self.execute(
                "CREATE TABLE ref("
                "id INTEGER PRIMARY KEY, "
                "source_id INTEGER NOT NULL, "
                "child_id INTEGER NOT NULL, "
                "parent_id INTEGER, "
                "FOREIGN KEY(source_id) REFERENCES source(id) ON DELETE "
                "CASCADE, "
                "FOREIGN KEY(child_id) REFERENCES article(id) ON DELETE "
                "CASCADE, "
                "FOREIGN KEY(parent_id) REFERENCES article(id) ON DELETE "
                "CASCADE, "
                "UNIQUE(child_id, parent_id), "
                "CHECK (child_id != parent_id))")

            # Create the duplicate detection trigger for references.
            self.execute(
                "CREATE TRIGGER ref_dup_check BEFORE INSERT ON ref "
                "WHEN NEW.parent_id IS NULL BEGIN SELECT "
                "RAISE(ABORT, 'Duplicated article/source reference.') "
                "WHERE EXISTS (SELECT * FROM ref "
                "WHERE source_id=NEW.source_id "
                "AND child_id=NEW.child_id LIMIT 1); END;")

            # Creating the auto delete trigger for deleting a reference with
            # the same source as an added link
            self.execute(
                "CREATE TRIGGER ref_clean AFTER INSERT on ref "
                "WHEN NEW.parent_id IS NOT NULL BEGIN "
                "DELETE FROM ref WHERE "
                "source_id=NEW.source_id AND child_id=NEW.child_id "
                "AND parent_id IS NULL; END;")

            # Create the trigger that prevents adding a reference from an
            # article to its publisher source.
            self.execute(
                "CREATE TRIGGER ref_source_check BEFORE INSERT ON ref "
                "BEGIN "
                "SELECT RAISE(ABORT, "
                "'Reference source and article source are the same.') "
                "WHERE EXISTS (SELECT * FROM article WHERE "
                "id = NEW.child_id AND source_id = NEW.source_id); "
                "END;")
        except sqlite3.OperationalError:
            # Tables already exist.
            pass

    def execute(self, query, params=()):
        """(Database, str, tuple) -> Bool
        Executes the given query, and commits it to the database. Returns
        True if the query was executed, and False otherwise.
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def query(self, model, query, params=(), convert=True):
        """(Database, Model, str, tuple, Bool) -> [Model] or [dict]
        Executes a query on the database. If convert is True, the database
        returns the results as a list of models that match the type of the
        given model, for the query given. If convert is False, the database
        returns a list of dictionaries for the given query. If the query
        succeeded the list is non-empty in both cases. If the returned list
        was non-empty, then the query was either invalid, or there were no
        rows to return.
        """
        try:
            # Get the list of dictionaries from the database.
            rows = self.cursor.execute(query, params).fetchall()

            # Convert those into objects with the type that model has, if
            # conversion is specified
            if convert:
                for i in range(0, len(rows)):
                    # Create the object and update its internal state.
                    object = model()
                    object.__dict__.update(rows[i])

                    # Replace the row with the object.
                    rows[i] = object

            # Return the list of objects.
            return rows
        except sqlite3.IntegrityError:
            return []

    def _add(self, object):
        """(Model) -> Bool
        Adds an object to the database, or modifies an existing one. Return
        True if the object was added or modified, or False otherwise.
        """
        # Get the attributes from the object matching the fields given.
        fields = object.db_fields.split(',')
        params = []
        for field in fields:
            # Get the value from the class, and add it to the parameters list
            params.append(getattr(object, field.strip()))

        # Create the comma separated list of question marks, used in the
        # query specification for sqlite.
        sub = ('?, ' * len(fields))[:-2]

        # ...and convert it to a tuple so sqlite understands it.
        params = tuple(params)

        # Execute the insertion or replace for the object given
        return self.execute(
            'INSERT OR REPLACE INTO %s(%s) VALUES (%s)' %
            (object.db_table, object.db_fields, sub), params)

    def add_article(self, article, add_source=True):
        """(Database, Article) -> Bool
        Adds the article to the database. Returns True if the article was
        added, and False otherwise. If add_source is True, then the source
        is added if the source does not already exist.
        """
        # Check if the source is in the database.
        temp_source = Source(article.url)
        source = self.get_sources(url=temp_source.url).first()
        if source is None:
            if add_source:
                # Add the source if it doesn't exist
                self.add_source(temp_source)

                # Try adding the article again, but don't get stuck in a
                # failure loop
                return self.add_article(article, False)
            else:
                # The article's source must explicitly be in the database to
                # add the article.
                return False

        # Add the article to the database.
        article.source_id = source.id
        return self._add(article)

    def add_keyword(self, keyword):
        """(Database, Keyword) -> Bool
        Adds a keyword the database. Return True if the keyword was added,
        and False if otherwise.
        """
        return self._add(keyword)

    def add_reference(self, reference):
        """(Database, Reference) -> Bool
        Adds a reference to the database. Returns True if the reference was
        added, and False otherwise. Automatically determines the source if
        it was a reference between a child and parent article.
        """
        if reference.parent_id and reference.parent_id != -1:
            # This a reference between a child and parent article, determine
            # the source automatically.
            article = self.get_by_id(Article, reference.parent_id)
            reference.source_id = article.source_id

        return self._add(reference)

    def add_source(self, source):
        """(Database, Source) -> Bool
        Adds the source to the database. Returns True if the source was
        added, and False otherwise.
        """
        return self._add(source)

    def add_watch(self, watch):
        """(Database, Watch) -> Bool
        Adds the watch to the database. Returns True if the watch was
        added, and False otherwise.
        """
        return self._add(watch)

    def delete_by_id(self, model, id):
        """(Database, Model, int) -> Bool
        Deletes an object from the database, if the object has the given id.
        Returns True if the object was deleted or didn't exist, and False if
        the query was invalid.
        """
        return self.execute('DELETE FROM %s WHERE %s.id=?' %
                            (model.db_table, model.db_table),
                            (id, ))

    def get_by_id(self, model, id):
        """(Database, Model, int) -> dict
        For the given id, returns a dictionary with values associated with
        the Model. If there was no object in the database matching the id,
        returns None.
        """
        # Query the database for the object with the given id.
        rows = self.query(
            model,
            "SELECT %s FROM %s WHERE %s.id = ?" %
            (model.db_labels, model.db_from, model.db_table), (id, ))

        # Query returns a list, so select the first element.
        if rows:
            return rows[0]
        else:
            return None

    def get_articles(self, url='', title='', author='', tags='',
                     date_start='', date_end='', query='',
                     source_id=None):
        """(Database, str, str, str, str, str, str, Bool, str, int) -> Query
        Returns the query for the given combination of filters. Query is the
        filter that checks multiple columns for matching values.
        """
        # Add each filter and parameter if a value was given for it.
        filters = []
        params = []

        if url:
            filters.append('article.url LIKE ?')
            params.append(url)

        if title:
            filters.append('article.title LIKE ?')
            params.append(title)

        if author:
            filters.append('article.author LIKE ?')
            params.append(author)

        if tags:
            # Tags are a comma separated list, so split them
            tag_list = tags.split(',')

            # Add each tag under a grouped query that checks for each one
            # in the column
            tag_filters = ['article.tags LIKE ? '] * len(tag_list)
            tag_filters = "OR ".join(tag_filters)
            filters.append('(%s)' % tag_filters)
            params += tags

        if date_start:
            filters.append('article.date >= ?')
            params.append(date_start)

        if date_end:
            filters.append('article.date <= ?')
            params.append(date_end)

        if query:
            filters.append('(article.url LIKE ? OR article.title LIKE ? or '
                           'article.date LIKE ? OR article.author LIKE ? or '
                           'article.tags LIKE ?)')
            params += [query, query, query, query, query]

        if source_id:
            filters.append('article.source_id = ?')
            params.append(source_id)

        return Query(self, Article, filters, params)

    def get_keywords(self, source_id=None, name=''):
        """(Database, str) -> Query
        Returns the query for the given combination of filters.
        """
        filters = []
        params = []

        if source_id:
            filters.append('keyword.source_id = ?')
            params.append(source_id)

        if name:
            filters.append('keyword.name LIKE ?')
            params.append(name)

        return Query(self, Keyword, filters, params)

    def get_references(self, child_id=None, source_id=None, parent_id=None,
                       sources=None):
        """(Database, int, int, int, [Source]) -> Query
        Returns the list of references for a given article id.
        """
        filters = []
        params = []

        if child_id:
            filters.append('ref.child_id = ?')
            params.append(child_id)

        if source_id:
            filters.append('ref.source_id = ?')
            params.append(source_id)

        if parent_id:
            filters.append('ref.parent_id = ?')
            params.append(parent_id)

        if sources:
            # Sources are a list of source objects. We want to filter by
            # their ids, so add them to a list.
            ids = []
            for source in sources:
                ids.append(source.id)

            # Generate the filter query.
            if ids:
                id_filters = ['ref.source_id = ? '] * len(ids)
                id_filters = "OR ".join(id_filters)
                filters.append('(%s)' % id_filters)
                params += ids

        return Query(self, Reference, filters, params)

    def get_sources(self, url='', urls=None):
        """(Database, str, [str]) -> Query
        Returns the query for the given combination of filters.
        """
        filters = []
        params = []

        if url:
            filters.append('source.url LIKE ?')
            params.append(url)

        if urls:
            # Urls are given as a list of strings.
            url_filters = ['source.url = ?'] * len(urls)
            url.filters = "OR ".join(url_filters)
            filters.append('(%s)' % url_filters)
            params += urls

        return Query(self, Source, filters, params)

    def get_watches(self, url='', domain=''):
        """(Database, str, str) -> Query
        Returns the query for the given combination of filters.
        """
        filters = []
        params = []

        if url:
            filters.append('watch.url LIKE ?')
            params.append(url)

        if domain:
            filters.append('watch.domain LIKE ?')
            filters.append(domain)

        return Query(self, Watch, filters, params)


def row_to_dict(cursor, row):
    """(cursor, row) -> dict
    Returns a dict from an sqlite3 row. From the sqlite3 docs
    on python.org."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

if __name__ == "__main__":
    # Create the database and the tables.
    db = Database(':memory:')
    db.create_tables()

    # Insert stuff into the tables
    # db.add(Source("http://www.cnn.com"))
    print (db.add_article(Article('http://www.cnn.com/test1', 'Test')))
    print (db.add_article(Article('http://www.cnn.com/test1', 'Test 2')))
    print (db.add_article(Article('http://www.bbc.com/test3', 'Test 3')))
    print (db.get_articles().all())