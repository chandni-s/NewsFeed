from model import Model
from tld import get_tld


class Source(Model):
    """A source is a producer or publisher of news pieces, referred to as
    Articles in this application. They are uniquely represented by their URL.
    """
    db_table = "source"
    db_from = "source"
    db_fields = "id, url"
    db_labels = "source.id, source.url"

    def __init__(self, url=''):
        """(Source, str) -> None
        Constructs a source. If given a non-empty URL, the URL is parsed to
        just get the base domain name (for example, http://google.com becomes
        just google.com).
        """
        # Parse the URL to get the base domain name, if the URL is non-empty
        if url:
            if not url.startswith('http://') and not url.startswith(
                    'https://'):
                # Append http:// if the URL doesn't start with it
                self.url = get_tld('http://' + url)
            else:
                # Take the address as is
                self.url = get_tld(url)

            # Ensure that the url starts as twitter.com
            if url.find("twitter") >= 0:
                url = url[url.find("twitter"):]

                # Include the name of the account if it exists
                if self.url.startswith("twitter.com"):
                    url = url.split("/")
                    index = url.index("twitter.com")
                    self.url = url[index]

                    # Confirm that there is an account name
                    if index < len(url) - 1:
                        self.url += "/" + url[index + 1]

                # Remove the leading "/"
                if self.url[-1] == "/":
                    self.url = self.url[:-1]


        else:
            self.url = None

        # Database fields.
        self.id = None