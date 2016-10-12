from model import Model


class Article(Model):
    """An article is a news piece written by a source. It is uniquely
    identified by its URL.
    """
    db_table = "article"
    db_from = "article JOIN source ON article.source_id = source.id"
    db_fields = "id, source_id, url, title, date, author, tags"
    db_labels = "article.id, source.id as source_id, source.url as source, " \
                "article.url as url, article.title, article.date, " \
                "article.author, article.tags"

    def __init__(self, url='', title='', date='', author='', tags='',
                 watched=False):
        """(Article, str, str, str, str, str, Bool) -> None
        Constructs the article with the given parameters. Strips whitespace
        from the fields.
        """
        # Constructor fields.
        self.url = url.strip() if url else ''
        self.title = title.strip() if title else ''
        self.date = date.strip() if date else ''
        self.author = author.strip() if author else ''
        self.tags = tags.strip() if tags else ''
        self.watched = watched

        # If the title field is the empty string, change it to a None so the
        # database throws errors about titles consisting of just spaces.
        if not self.title:
            self.title = None

        # Database fields.
        self.id = None
        self.source_id = None
        self.source = None
