from bs4 import BeautifulSoup
from tld.exceptions import TldDomainNotFound, TldBadUrl
from dateutil import parser
from database import Database
from article import Article
from reference import Reference
import requests

# Set invalid page type, 
NO_EXTS = ['mp3', 'jpg', 'gif', 'xml', 'jpeg', 'mp4',
                        'wma', 'pdf']
def crawl_site(database, url, depth=1):
    """(Database, str, int) -> [Article]
    Crawls the given URL, and returns a list of articles that have been parsed
    and added to the database. Depth can be used to limit how far the
    crawl will go.
    """
    if not url or depth <= 0:
        print "depth <= 0"
        return []    
    
    # check the page time, and if it is an uncheckable page time, then stop parsing
    for ext in NO_EXTS:
        if url.endswith("." + ext):
            return []          
    # Get the web page from the given url.
    try:
        page = requests.get(url)
        page = BeautifulSoup(page.text)
    except:
        return []
    articles=[]
    # Iterate over every URL in the page, looking for articles.
    checked_urls = []
    if page.a != None:
        for article in page.find_all('a'):
            # Don't check articles we've already checked.
            link = article.get('href')
            if link not in checked_urls:
                cur_article = database.get_articles(url=link).first()
                if depth > 1:
                    if cur_article is None:                
                # Try parsing the article, and then add the articles obtained to
                # the full list.
                        articles += crawl_url(database, url=link, depth=depth)
                       
                    articles += crawl_site(database, link, depth-1)
                
                # Add the article to the checked list.
                checked_urls.append(link)

    # Return all articles that have been added to the database.
    return articles


def crawl_url(database, url, parent='', date='', verify=True, depth=1):
    """(Database, str, str, str, Bool, int) -> [Article]
    Parses the given url to generate an Article. The article is then added to
    the database, along with any references to existing objects within the database.
    If  URLs are found within the article, then the crawl_url is called
    recursively on them until a depth of 0 is reached.

    Returns the list of articles that have been added to the database during the crawl.
    """
    # If the URL is empty, or the crawl has gone too deep, stop.
    if not url or depth <= 0:
        print "Couldn't fetch: %s" % url
        return []

    # check the page time, and if it is an uncheckable page time, then stop parsing
    for ext in NO_EXTS:
        if url.endswith("." + ext):
            return []      
    # Get the web page from the given url.
    try:
        request = requests.get(url)
        page = BeautifulSoup(request.text)
    except:
        # Couldn't fetch article.
        return []

    # If verification is requested, then try doing a verification of whether the page is actually an article, using the
    # opengraph type
    if verify:
        try:
            if (page.find("meta", {"content": "article"}) is None):
                print "Not an article: %s" % url
                return []
        except:
            return []

    article = database.get_articles(url=url).first()
    if article is None:
        # Find the page's publish date and author.
        author = ''
        for meta in page.find_all('meta'):
            if 'name' in meta.attrs and 'content' in meta.attrs:
                # If the name of the metadata tag looks like a publish date, or
                # a last modify date, that's likely the date of the page.
                name = meta.attrs['name'].lower()
                if not date:
                    if 'date' in name or 'mod' in name or 'pub' in name:
                        # Try parsing the date. The date may come in many
                        # formats, or may not be a date at all, so it's
                        # parsed using dateutil.
                        value = meta.attrs['content']
                        try:
                            date = parser.parse(value).strftime('%Y-%m-%d')
                        except:
                            pass

                # If the name of the metadata tag looks like an author, then
                # take the value.
                if not author and 'author' in name:
                    author = meta.attrs['content']

        # If there was no date, then look within the last modified html header.
        if not date:
            if 'last-modified' in request.headers:
                try:
                    date = parser.parse(
                        request.headers['last-modified']).strftime('%Y-%m-%d')
                except:
                    pass

        # If there was no title, this page is unlikely an article.
        if page.title is None:
            print "Not an article: %s" % url
            return []

        # Get the article title.
        title = page.title.string

        # Add the article to the database. The URL might be malformed, so handle
        # exceptions coming from the tld library.
        try:
            database.add_article(Article(url=url, title=title, date=date,
                                         author=author))
        except (TldDomainNotFound, TldBadUrl):
            print "Could not add article: %s" % url
            return []

        # Get the added article from the database.
        article = database.get_articles(url=url).first()
    if article is None:
        # The article wasn't found, and the crawl can't continue.
        print "Could get article from database: %s" % url
        return []

    # If given a parent article URL, then create a reference to it.
    if parent:
        parent_article = database.get_articles(url=parent).first()
        if parent_article is not None:
            database.add_reference(
                Reference(child_id=article.id, parent_id=parent_article.id))

    # The list of added articles is initially just the current article.
    articles = [article]

    # Look through the page content for URLs to crawl, and references.
    checked_words = []
    checked_urls = []
    for content in page.find_all('p'):
        # Find all the link tags in the given block, to look for references
        # and pages to crawl.
        tags = BeautifulSoup(str(content))
        if tags.a:
            for tag in tags.find_all('a'):
                # Extract the URL from the tag.
                sub_url = tag.get('href')

                # If the link hasn't been checked already, check if there's
                # an existing article in the database with that url.
                if sub_url not in checked_urls:
                    ref_article = database.get_articles(url=sub_url).first()
                    if ref_article is None:
                        # Crawl the page, it's not already in the database and
                        # there is still remaining depth to crawl. Append the
                        # results to the list of currently added articles.
                        if depth > 1:
                            articles += crawl_url(database, sub_url, url,
                                                  depth=depth-1)
                    else:
                        # The article exists in the database. Create a
                        # reference between this article and the referenced
                        # one.
                        database.add_reference(
                            (Reference(child_id=article.id,
                                       parent_id=ref_article.id)))

                    # Add the URL to the checked list, so it isn't checked
                    # again.
                    checked_urls.append(sub_url)

        # Look for references to Sources by checking keywords in the database.
        words = unicode(content.getText()).split()
        for word in words:
            # Only check the word if it hasn't been checked before.
            if word not in checked_words:
                # Check the database for a keyword that matches the current
                # word.
                keyword = database.get_keywords(name=word).first()
                if keyword is not None:
                    # The keyword exists in the database, create a reference
                    # between the source of the keyword, and the article.
                    database.add_reference(
                        Reference(child_id=article.id,
                                  source_id=keyword.source_id))

                # Add the word to the checked words list, so it isn't
                # checked again.
                checked_words.append(word)

    # Return the list of articles that have been added to the database.
    return articles

if __name__ == "__main__":
    db = Database(':memory:')
    db.create_tables()
    test_site = crawl_site(db, 'http://cbc.ca/', 3)
    print test_site 
    print len(test_site)
    # print crawl_url(db, 'http://www.cnn.com', depth=2)
