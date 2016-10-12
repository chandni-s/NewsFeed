from model import Model
from tld import get_tld


class Watch(Model):
    """A watch is a URL that contains other links to URLs that contain
    articles, or other pages that contain article. Watches are used to crawl
    the web periodically for new content for the application.
    """
    db_table = "watch"
    db_from = "watch"
    db_fields = "id, url, domain"
    db_labels = "watch.id, watch.url, watch.domain"

    def __init__(self, url=''):
        """(Watch, str) -> None
        Constructs a watch. If given a non-empty URL, the URL is parsed to
        just get the base domain name (for example, http://google.com becomes
        just google.com).
        """
        # Parse the URL to get the base domain name, if the URL is non-empty
        if url:
            # Append http:// if the URL doesn't start with it
            if not url.startswith('http://') and not url.startswith(
                    'https://'):
                self.url = 'http://' + url
            else:
                self.url = url

            # Store the domain.
            self.domain = get_tld(self.url)
        else:
            self.url = None
            self.domain = None

        # Database fields.
        self.id = None