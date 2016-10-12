from model import Model


class Keyword(Model):
    """A keyword is an alternate name for a source. It is used when searching
    for references within articles, so each keyword must be uniquely
    identified by its name.
    """
    db_table = "keyword"
    db_from = "(SELECT keyword.id, keyword.source_id, keyword.name, " \
              "source.url FROM " \
              "keyword LEFT JOIN source ON keyword.source_id = " \
              "source.id) AS keyword "
    db_fields = "id, source_id, name"
    db_labels = "id, source_id, name, " \
                "(coalesce(url, '')) as source"

    def __init__(self, source_id=None, name=''):
        """(Source, str) -> None
        Constructs a keyword using a source id, and the keyword name.
        Whitespace is stripped from the keyword name.
        """
        # Constructor fields.
        self.source_id = source_id
        self.name = name.strip()

        # If the name field is the empty string, change it to a None so the
        # database throws errors about names consisting of just spaces.
        if not self.name:
            self.name = None

        # Database fields
        self.id = None
        self.source = None