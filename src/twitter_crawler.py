import twython
import datetime
import time

from dateutil import parser
from database import Database
from article import Article
from keywords import Keyword
from reference import Reference
from source import Source
from bs4 import BeautifulSoup
import requests
import os

def twi_time_convert(timestr):
    """(str) -> str
    Convert time str from ctime format to isoformat,
    i.e. TWed Nov 26 01:45:12 +0000 2014 -> 20141126
    
    Return the given time str in iso-time format, or an empty string 
    if the given format is invalid.
    """
    try:
        # Analyse given time str to seperate elements.
        struct_time = time.strptime(timestr[:-10]+timestr[-4:], "%a %b %d %H:%M:%S %Y")
        # Convert given time by secend unit.
        t = time.mktime(struct_time) 
        # Re-construct time to isotime format.
        isot = time.strftime("%Y%m%d", time.gmtime(t))
        return isot
    
    except:
        return ''
    

def article_to_db(database, url, parent='', date='', verify=True, depth=1):
    """(Database, str) -> list
    Add the article of the given url to database.
    Return the list contains the single article, or an empty list if it cannot
    be added. (The reason to return list is for consistency with article & site 
    clawler)
    """
    if not url:
        return []
    try:
        page = requests.get(url)
        page = BeautifulSoup(page.text)
    except:
        # Couldn't fetch article.
        return []
    verify = page.find("meta", {"content":"article"})
    if verify == None:
        return []
    else:
        article = database.get_articles(url=url).first()
        if article is None:        
            # Find the page's publish date and author.
            author = ''
            for meta in page.find_all('meta'):
                if 'name' in meta.attrs and 'content' in meta.attrs:
                    # If the name of the metadata tag looks like a publish date, or
                    # a last modify date, that's likely the date of the page.
                    name = meta.attrs['name'].lower()
                    if not date and 'date' in name or 'mod' in name:
                        # Try parsing the date. The date may come in many formats,
                        # or may not be a date at all, so it's parsed using dateutil.
                        value = meta.attrs['content']
                        try:
                            date = parser.parse(value).strftime('%Y-%m-%d')
                        except:
                            pass
        
                    # If the name of the metadata tag looks like an author, then take
                    # the value.
                    if not author and 'author' in name:
                        author = meta.attrs['content'] 
            if page.title is None:
                return []
            title = page.title.string
            # Add the article to the database. The URL might be malformed, so handle
            # exceptions coming from the tld library.            
            try:
                database.add_article(Article(url=url, title=title, date=date,
                                             author=author))
            except (TldDomainNotFound, TldBadUrl):
                return [] 
            article = database.get_articles(url=url).first()
        if article is None:
            # The article wasn't found, and the crawl can't continue.
            return [] 
        else: 
            return [article]
        

def search_references(database, tweet_html, tweet_id):
    """(Database, str, int) -> list[Article]
    Search the link & keyword references inside the given tweet html.
    Add the founded reference articles and references into database.
    Return the list of added articles.
    """
    try:
        tweet = BeautifulSoup(tweet_html)
    except:
        # Couldn't fetch article.
        return []  
    
    checked_words = []
    checked_urls = []
    articles = []
    if tweet.a != None:
        # Check all words with mention tag, which indicate another twitter account
        for at in tweet.find_all('a', {'class': 'twython-mention'}):
            account = at.text
            # Add the twitter account as a Source
            source_url = "twitter.com/" + account[1:]
            database.add_source(Source(source_url))

            database.get_by_id(Source, 1)

            check = database.get_sources(url=source_url)
            # Add corresponding keywords for the account for reference searching
            if check.count() != 0:
                s_id = check.first().id
                database.add_keyword(Keyword(s_id, account))
                # Should include the other case: #username
                database.add_keyword(Keyword(s_id, "#"+account[1:]))
        # find all hyperlinks in tweet content
        for atag in tweet.find_all('a', {'class': 'twython-url'}):
            t_url = atag.get('href')
            # If the link hasn't been checked already, check if there's
            # an existing article in the database with that url.            
            if t_url not in checked_urls:
                ref_article = database.get_articles(url=t_url).first()
                if ref_article is None:
                    articles += article_to_db(database, t_url)
                ref_article = database.get_articles(url=t_url).first()
                if ref_article != None:
                    # Make sure the article exists in the database. Create a
                    # reference between this article and the referenced 
                    # one.                    
                    database.add_reference(
                                (Reference(child_id=tweet_id,
                                           parent_id=ref_article.id)))

                # Add the URL to the checked list, so it isn't checked
                # again.
                checked_urls.append(t_url)                    
    
    # Look for references to Sources by checking keywords in the database.
    words = unicode(tweet.getText()).split()
    # Get all the keywors in database, those are the possible reference keywods
    # i.e. all the TWITTER account need to be added to database as a source with
    # corresponding keywords.
    keywords = database.get_keywords().all()

    for word in words:
        #print word
        # Only check the word if it hasn't been checked before.
        if word not in checked_words:
            check = database.get_keywords(name=word)
            if check.count() != 0:
                ref_source = check.first().source_id
                # This word is one of the keyword existed in database, create a
                #reference between the source of the keyword, and the article.
                database.add_reference(
                    Reference(child_id=tweet_id,
                              source_id=ref_source))

            # Add the word to the checked words list, so it isn't
            # checked again.
            checked_words.append(word)    
            
    # Return the list of articles added to the database.        
    return articles


class TweeStreamer(twython.TwythonStreamer):
    """Twitter API listener class for catching updating tweets."""
    def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, 
                 database):
        """(TweeStreamer, str, str, str, str, Database) -> None
        Set up the Twitter usr account with authentication information, and define
        the database for data adding.
        """
        # Call parent class __init__ for basic setup.
        super(TweeStreamer, self).__init__(app_key, app_secret, oauth_token, 
                                           oauth_token_secret)
        self.database = database
        
        
    def on_success(self, data):
        """(TweeStreamer, TweetData) -> list[Article]
        When the streamer catches a new tweet, add the tweet as an article to 
        database. Search the references in the tweet content, add references and
        reference articles in to database.
        Return the added Articles. 
        """       
        # the parameter of this function is fixed, so need a global DB to call
        # Again, need to make sure all the watched tweeter account have been 
        # added to database as a source and corresponding keywaord name.
   
        # get the author name of the specific tweet
        t_author = data['user']['screen_name']
        ref_articles = []
        
        t_time = twi_time_convert(data['created_at'])

        # Generate a fake url for tweet article, since the database requires
        # every Article object must have an unique url.
        t_url = 'twitter.com/' +  t_author + '/' \
            + t_time + '/'
        t_date = t_time[:4] + '-' + t_time[4:6] + '-' + t_time[6:8]
  
        content = data['text']
        print "-------------------------"
        print content
        # The article title is whole content of tweet
        
        #t_article = Article(url=t_url, title=content, 
                            #date=t_date, author= t_author)
                            

        #print t_article
        add_t =self.database.add_article(Article(url=t_url, title=content, 
                            date=t_date, author= t_author))
   
        
        if add_t == True:

            # When make sure the tweet article is in database, call helper 
            # function to search references inside tweet content.
            tweet_id = self.database.get_articles(title=content).first().id  
            # Convert to html type for link analyzing.
            tweet_html = twython.Twython.html_for_tweet(data)
            
            ref_articles += search_references(self.database, tweet_html, tweet_id)
            
            refs = self.database.get_references(tweet_id)
            if refs.count() != 0:
                print ">>>>>>>>>>>>>>>>>>>>>>>>>"
                print refs.all()   
        return ref_articles
                
       
    def on_error(self, status_code, data):
        """(TweeStreamer, int, TweetData) -> None
        When error appears, print(??or return) error code to indicate the issue.
        """
        print(status_code)

        # If still want to stop trying to get data because of the error,
        # Then UNCOMMENT the next line
        self.disconnect()    


def get_twitters():
    """None -> list[str]
    From database get all the Twitter account names that need to follow.
    """
    # Please help me for this feature, I don't have a clear idea since we 
    # haven't had a certain plan for how to define the twitter sources.
    pass

def set_up_streamer(consumer_key, consumer_secret, 
                    access_token, access_token_secret, database, focus="e"):
    """(str, str, str, str) -> list[Article]
    Set up all the twitter accounts we need to follow. Analyze their posted 
    tweets for references, and add them to streamer's watchlist for further 
    updating.
    Return the added Articles during analyzing accounts' posted tweets.
    """
    # Set up an authentication twython user.
    twitter = twython.Twython(consumer_key, consumer_secret,
                      access_token, access_token_secret) 
    # Get all the twitter account need to analyze
    #follows = get_twitters()
    # Dictionary for account name-account id
    account_id = {}
    ref_articles = []
    
    # Create a Streamer to catch updated tweets from target twitter accounts.    
    t_stream = TweeStreamer(consumer_key, consumer_secret,
              access_token, access_token_secret, database = database)

    #t_stream.statuses.filter(follow=follow_ids)
    t_stream.statuses.filter(track=focus)
    # Not sure whether need the article list, since it doesn't include the 
    # new articles added by streamer.
    return ref_articles 



if __name__ == "__main__":
    # here is a sample that returned by "twython.Twython.html_for_tweet(tweet)"
    tweet_html1= '<a href="http://www.cbc.ca/news/canada/saskatoon/jennifer-huculak-kimmel-s-1m-baby-bill-denied-by-saskatchewan-blue-cross-1.2847097" class="twython-url">google.com</a> is a NBC <a href="https://twitter.com/search?q=%23cool" class="twython-hashtag">#cool</a> site, lol! CBC <a href="https://twitter.com/miranda" class="twython-mention">@miranda</a> should <a href="https://twitter.com/search?q=%23checkitout" class="twython-hashtag">#checkitout</a>. If you can! <a href="https://twitter.com/search?q=%23thanks" class="twython-hashtag">#thanks</a> RTL ove, <a href="https://twitter.com/__twython__" class="twython-mention">@__twython__</a> <a href="https://t.co/67pwRvY6z9" class="twython-url">github.com</a>'
    
    # Twitter for testing: name=team01
    consumer_key = 'nJaVfIASrz2XIcBoktOjibvf7'
    consumer_secret = 'ZXVxuyNBv2w5BGyx8IkZmQLgYf6ETRybz7lywpm6FCYIheLrTd'
    access_token = '2691084998-3PLdg836PRc3PvxqlSesRl9Q2ThJIWvWlUBxsHM'
    access_token_secret = 'yUDOjEA5qB8V3a9Xrkhjvzxng70YGEtYEEohTUyIrD9Lt'
    db = Database('test_twit')
    db.create_tables()   
    t = twython.Twython(consumer_key, consumer_secret,
                          access_token, access_token_secret) 
   
    
    set_up_streamer(consumer_key, consumer_secret, 
                            access_token, access_token_secret, db, 'Israel') 
                            
    
     
    db.close()
    
    os.remove("test_twit")    