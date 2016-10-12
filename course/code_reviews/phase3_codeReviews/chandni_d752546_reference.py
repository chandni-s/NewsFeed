from model import Model


class Reference(Model):
    """A reference is a link between a child article and a parent article,
    or a citation between an article and a source.
    """
    db_table = "ref"
    db_from = "(SELECT ref.id, ref.child_id, ref.parent_id, " \
              "ref.source_id, source.url FROM " \
              "ref INNER JOIN source ON ref.source_id = source.id) AS ref " \
              "LEFT JOIN article ON ref.parent_id = article.id "
    db_fields = "id, child_id, source_id, parent_id"
    db_labels = "ref.id as id, ref.child_id as child_id, " \
                "ref.source_id as source_id, ref.parent_id as parent_id, " \
                "(coalesce(article.title, '')) as parent_title, " \
                "article.url as parent_url, ref.url as source_url," \
                "(coalesce(article.url, ref.url)) as reference"

    def __init__(self, child_id=None, source_id=None, parent_id=None):
        """(Reference, int, int, int) -> None
        Constructs the reference with the parameters given.
        """
        # Constructor parameters.
        self.child_id = child_id
        self.source_id = source_id
        self.parent_id = parent_id

        # Database fields.
        self.id = None
        self.parent_title = None
        self.parent_url = None
        self.source_url = None
        self.reference = None
