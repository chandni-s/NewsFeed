class Model():
    """A database model. Objects that interact with the database (add, get,
    delete, etc...) should be derived from this class. This helps create a
    consistent interface for the database to use to implement its functions
    (and prevents lots of repetition in queries as a bonus)."""

    # (str)
    # The table name for the class.
    db_table = ""

    # (str)
    # The name of the members of the class that the database stores. The
    # class must have every field listed in this string after renaming
    # columns, or the conversion from dict to the Model will fail.
    db_fields = ""

    # (str)
    # The labels to use after performing select operations. It is important
    # that these match all required elements in the constructor of the
    # class, since a conversion from a database row (represented by a
    # dictionary) to the constructor parameters happens after getting rows
    # from the database.
    db_labels = ""

    # (str)
    # Where to get the data for the class from. May contain joins onto other
    # tables.
    db_from = ""

    def __repr__(self):
        """(Model) -> str
        Returns the string representation of a model.
        """
        # Convert the internal dictionary into something that looks like a
        # parameter to list, for better readability.
        params = []
        for k, v in self.__dict__.iteritems():
            params.append('%s=%r' % (k, v))
        params = ", ".join(params)

        return "%s(%s)" % (self.__class__.__name__, params)
