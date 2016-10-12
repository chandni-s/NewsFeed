#
# server.py
#
# When run, handles interaction between the backend of the application
# (database, tasks, etc) with the user interface front end of the application.
# It does this by creating a web server, and handling requests.
#
# Flask documentation (http://flask.pocoo.org/docs/0.10/) does a good job of
# explaining some of the basic concepts for how to interact with the web
# server. The server starts on the local network, and routes addresses given
# from the browser to python functions. These functions then return some text
# content to the browser.
#
# GET requests from the UI have parameters, and can be accessed through
# request.args.get(...). Although functions return text, the UI interacts with
# the server through JavaScript, and formatting objects to JSON first makes
# UI interaction easier. For this reason, all functions that respond to
# GET requests will return JSON.
#
# To make handling JSON responses easier and more consistent, the Response
# class is used throughout.
#
# For the database, connections may be split across multiple threads, and the
# sqlite3 requires that a connection stay on a single thread. Flask has
# functionality that assists in only connecting to the database whenever
# necessary, and we make use of that with the get_db function (and the
# close_db function, but that does not need to be called directly).
#
from flask import Flask, render_template, request, g
from tld import update_tld_names
from tld.exceptions import TldDomainNotFound, TldBadUrl
from urllib2 import unquote
from updater import Updater
from database import Database
from article import Article
from source import Source
from reference import Reference
from keywords import Keyword
from response import Response
import web


# Setup the Flask server, and route anything under the static folder for UI
# resource requests.
app = Flask(__name__, static_folder='static', template_folder='static',
            static_url_path='')

# Load default application configuration, but also override settings from
# the environment, if the variable exists.
app.config.update(dict(
    # The number of seconds to wait before performing another update of
    # watched articles, and RSS feeds.
    UPDATE_FREQUENCY=300,

    # The path to the database file.
    DATABASE='test.db',

    # Debug mode enables automatic source reloading.
    DEBUG=True
))
app.config.from_envvar('FLASK_SETTINGS', silent=True)


def get_db():
    """(None) -> Database
    Opens a new database connection if one is not already open."""
    if not hasattr(g, 'db'):
        g.db = Database(app.config['DATABASE'])
    return g.db


@app.teardown_appcontext
def close_db(_):
    """(Exception) -> None
    Closes the database at the end of a Flask request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/db/add_keyword')
def db_add_keyword():
    """(None) -> str
    Adds a keyword to a source.
    """
    # Construct the keyword and add it to the database
    keyword = Keyword(
        request.args.get('source_id', -1, type=int),
        request.args.get('name', '', type=str))

    db = get_db()
    if db.add_keyword(keyword):
        return Response(result=True, msg="Keyword added.").to_json()
    else:
        return Response(result=False, msg="Keyword already exists.").to_json()


@app.route('/db/add_reference')
def db_add_reference():
    """(None) -> str
    Adds a reference to an article.
    """
    ref = Reference(
        child_id=request.args.get('child_id', '', type=str),
        source_id=request.args.get('source_id', None, type=int),
        parent_id=request.args.get('parent_id', None, type=int))

    db = get_db()
    if db.add_reference(ref):
        return Response(result=True, msg="Referenced added.").to_json()
    else:
        return Response(result=False,
                        msg="A reference cannot reference itself.").to_json()


@app.route('/db/delete_article')
def db_delete_article():
    """(None) -> str
    Deletes an article, given by id."""
    id = request.args.get('id', None, type=int)
    db = get_db()
    if id > 0 and db.delete_by_id(Article, id):
        return Response(result=True, msg="Article deleted.").to_json()
    else:
        return Response(result=False, msg="No article selected.").to_json()


@app.route('/db/delete_keyword')
def db_delete_keyword():
    """(None) -> str
    Deletes a keyword, given by id.
    """
    id = request.args.get('id', None, type=int)
    db = get_db()
    if id > 0 and db.delete_by_id(Keyword, id):
        return Response(result=True, msg="Keyword deleted.").to_json()
    else:
        return Response(result=False, msg="No keyword selected.").to_json()


@app.route('/db/delete_reference')
def db_delete_reference():
    """(None) -> str
    Deletes a reference, given by id.
    """
    id = request.args.get('id', None, type=int)
    db = get_db()
    if id > 0 and db.delete_by_id(Reference, id):
        return Response(result=True, msg="Reference deleted.").to_json()
    else:
        return Response(result=False, msg="No reference selected.").to_json()


@app.route('/db/delete_source')
def db_delete_source():
    """(None) -> str
    Deletes a source, given by id.
    """
    id = request.args.get('id', None, type=int)
    db = get_db()
    if id > 0 and db.delete_by_id(Source, id):
        return Response(result=True, msg="Source deleted.").to_json()
    else:
        return Response(result=False, msg="No source selected.").to_json()


@app.route('/db/articles.xml')
def db_export_articles():
    """(None) -> str
    Exports articles from the database.
    """
    return ''


@app.route('/db/get_article')
def db_get_article():
    """(None) -> str
    Gets data for a single article, given by id.
    """
    db = get_db()
    article = db.get_by_id(Article, request.args.get('id', -1, type=int))
    if article:
        return Response(result=True, data=article).to_json()
    else:
        return Response(result=False, msg="Article does not exist.").to_json()


@app.route('/db/get_articles')
def db_get_articles():
    """(None) -> str
    Gets the articles that match the given query paramaters..
    """
    # Get the articles query for the given parameters.
    db = get_db()
    query = db.get_articles(
        url=request.args.get('url', '', type=str),
        title=request.args.get('title', '', type=str),
        author=request.args.get('author', '', type=str),
        tags=request.args.get('tags', '', type=str),
        date_start=request.args.get('date_start', '', type=str),
        date_end=request.args.get('date_end', '', type=str),
        watched=request.args.get('watched', None, type=bool),
        query=request.args.get('query', '', type=str))

    # Get the total number of articles in the filtered query.
    total = query.count()

    # Get the articles from the query, ordering by date descending.
    articles = query.subset(request.args.get('offset', 0, type=int),
                            request.args.get('length', 10, type=int),
                            by='date',
                            asc=False)

    # Give the articles, and the filtered count to the user interface.
    return Response(result=True,
                    data=articles,
                    params={'total': total}).to_json()


@app.route('/db/get_keywords')
def db_get_keywords():
    """(None) -> str
    Gets the keywords for a source given by id.
    """
    # Get the keywords query for the given parameters.
    db = get_db()
    query = db.get_keywords(
        request.args.get('source_id', None, type=int))

    # Get the total number of keywords in the filtered query.
    total = query.count()

    # Get the keywords from the query.
    keywords = query.subset(request.args.get('offset', 0, type=int),
                            request.args.get('length', 10, type=int))

    # Give the keywords, and the filtered count to the user interface.
    return Response(result=True,
                    data=keywords,
                    params={'total': total}).to_json()


@app.route('/db/get_references')
def db_get_references():
    """(None) -> str
    Gets the references for an article given by id.
    """
    # Get the references query for the given parameters.
    db = get_db()
    query = db.get_references(
        child_id=request.args.get('child_id', -1, type=int))

    # Get the total number of references in the filtered query.
    total = query.count()

    # Get the references from the query.
    references = query.subset(request.args.get('offset', 0, type=int),
                              request.args.get('length', 10, type=int),
                              by='reference')

    # Give the references, and the filtered count to the user interface.
    return Response(result=True,
                    data=references,
                    params={'total': total}).to_json()


@app.route('/db/get_source')
def db_get_source():
    """(None) -> str
    Gets data for a single source, given by id.
    """
    db = get_db()
    source = db.get_by_id(Source, request.args.get('id', -1, type=int))
    if source:
        return Response(result=True, data=source).to_json()
    else:
        return Response(result=False, msg="Source does not exist.").to_json()


@app.route('/db/get_sources')
def db_get_sources():
    """(None) -> str
    Gets the sources that match the given query.
    """
    # Get the sources query for the given parameters.
    db = get_db()
    query = db.get_sources(request.args.get('url', '', type=str))

    # Get the total number of sources in the filtered query.
    total = query.count()

    # Get the sources from the query.
    sources = query.subset(request.args.get('offset', 0, type=int),
                           request.args.get('length', 10, type=int),
                           by='url')

    # Give the sources, and the filtered count to the user interface.
    return Response(result=True,
                    data=sources,
                    params={'total': total}).to_json()


@app.route('/db/modify_article')
def db_modify_article():
    """(None) -> str
    Adds or modifies an article depending on the id given.
    """
    try:
        article = Article(
            request.args.get('url', '', type=str),
            request.args.get('title', '', type=str),
            request.args.get('date', '', type=str),
            request.args.get('author', '', type=str),
            request.args.get('tags', '', type=str))

        # Validate input
        if not article.url:
            return Response(result=False,
                            msg="Article requires a URL.").to_json()

        if not article.title:
            return Response(result=False,
                            msg="Article requires a title.").to_json()

        # If the id was -1, then convert it to None so it appears as a Null in
        # the database add query.
        id = request.args.get('id', None, type=int)
        if id == -1:
            id = None

        # id is not normally set in the constructor, so set it here.
        article.id = id

        db = get_db()

        if db.add_article(article):
            return Response(result=True, msg="Article saved.").to_json()
        else:
            return Response(result=False, msg="Article URL was not "
                                              "unique.").to_json()
    except (TldDomainNotFound, TldBadUrl):
        return Response(result=False,
                        msg="Article URL was not valid.").to_json()


@app.route('/db/modify_source')
def db_modify_source():
    """(None) -> str
    Adds or modifies an source depending on the id given.
    """
    try:
        source = Source(request.args.get('url', '', type=str))

        # Validate input
        if not source.url:
            return Response(result=False,
                            msg="Source requires a URL.").to_json()

        # If the id was -1, then convert it to None so it appears as a Null in
        # the database add query.
        id = request.args.get('id', None, type=int)
        if id == -1:
            id = None

        # id is not normally set in the constructor, so set it here.
        source.id = id

        db = get_db()
        if db.add_source(source):
            return Response(result=True, msg="Source saved.").to_json()
        else:
            return Response(result=False, msg="Source URL was not "
                                              "unique.").to_json()
    except (TldDomainNotFound, TldBadUrl):
        return Response(result=False,
                        msg="Source URL was not valid.").to_json()


@app.route('/db/toggle_watch')
def db_toggle_watch():
    """(None) -> str
    Toggles the watched state for an article given by id.
    """
    # Get the article given by id.
    db = get_db()
    article = db.get_by_id(Article, request.args.get('id', -1, type=int))
    if article is None:
        # Couldn't find the article, most likely no row was selected.
        return Response(result=False, msg="No article selected.").to_json()

    # Toggle the watch status.
    article.watched = not article.watched

    # Save the article in the database.
    if db.add_article(article, False):
        return Response(result=True, msg="Article watched.").to_json()
    else:
        return Response(result=True, msg="Article could not be "
                                         "watched.").to_json()


@app.route('/')
@app.route('/index.html', alias=True)
def render_index():
    """(None) -> str
    Renders the index page.
    """
    return render_template('index.html')


@app.route('/web/crawl_url')
def web_crawl_url():
    """(None) -> str
    Crawls the given URL for article content, references and new articles.
    Adds any articles it finds, and returns the list of added articles.
    """
    # Try decoding the encoded URL.
    try:
        url = unquote(request.args.get('url', '', type=str))
    except:
        return Response(result=False,
                        msg="Invalid URL given.").to_json()

    # Check how deep to crawl. If recursive was given as a option, and is
    # true, then the server crawls 3 articles deep.
    recursive = request.args.get('recursive', '', type=str)
    if recursive == 'true':
        depth = 3
    else:
        depth = 1

    # Crawl the given URL. If recursive was given as an option from the UI,
    # then it crawls up to 3 articles deep.
    db = get_db()
    articles = web.crawl_url(db, url, depth=depth)

    if articles:
        return Response(result=True,
                        msg="Found articles.",
                        data=articles,
                        params={'total': len(articles)}).to_json()
    else:
        return Response(result=False,
                        msg="Found no articles for the given URL.").to_json()


def update():
    """(None) -> None
    Updates the application's data.
    """
    # Get the flask application context, since this is running on a thread
    with app.app_context():
        print "test"

if __name__ == '__main__':
    # Update top level domains for URL checking.
    try:
        update_tld_names()
    except:
        pass

    # Create necessary tables for the database
    db = Database(app.config['DATABASE'])
    db.create_tables()
    db.close()

    # Start the updater thread
    # u = Updater(app.config['UPDATE_FREQUENCY'], update)
    # u.start()

    # Run the server
    app.run(debug=app.config['DEBUG'])
