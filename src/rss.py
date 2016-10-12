import feedparser
import requests
import datetime
import time
import os
from bs4 import BeautifulSoup
from tld.exceptions import TldDomainNotFound, TldBadUrl
from dateutil import parser
from database import Database
from article import Article
from keywords import Keyword
from reference import Reference
from web import crawl_url


def rss_feed(rss_url):    
    """(str) -> list(int, dict)
    Find all the updated article links in the RSS feed. 
    
    Return the total count of updated articles, and a dictionary with 
   (key: value)<->(aticle_link: publish_date in isotime format).
    """
    try:
        # Use feedparser to analyze given RSS feed, if it is valid RSS.
        d = feedparser.parse(rss_url)
    except:
        return "Sorry, invalid RSS feed. Please check and try again later."
    
    total = len(d['entries'])
    updates = dict()
    for index, item in enumerate(d['entries']):
        # Convert publish time from ctime format to iso-time format.
        a_time = time_convert(item.published)
        # Set article url ad dictionary key, with publish date as value. 
        updates[str(item.link)] = a_time        
    return (total, updates)


def time_convert(timestr):
    """(str) -> str
    Convert time str from ctime format to isoformat,
    i.e. Tue, 11 Nov 2014 17:58:48 EST -> 2014-11-11
    
    Return the given time str in iso-time format, or an empty string 
    if the given format is invalid.
    """
    
    try:
        # Analyse given time str to seperate elements.
        struct_time = time.strptime(timestr[:-4], "%a, %d %b %Y %H:%M:%S")
        # Convert given time by secend unit.
        t = time.mktime(struct_time) 
        # Re-construct time to isotime format.
        isot = time.strftime("%Y-%m-%d", time.gmtime(t))
        return isot
    
    except:
        return ''
    


def parse_rss(database, feed, depth=1):
    """(Database, str, int) -> [Article]
    Get all the updated article links in the RSS feed. 
    Find the reference inside all the articles recursively(set by "level"
    depth), and add the references into database.

    Return the total count of updated articles, and a dictionary with 
    (key: value)<->(aticle_link: publish_date in isotime format).
    """
    # Get the updates article count, and article urls and publish dates.
    rss_a = rss_feed(feed)
    
    # Get all (article urls, publish dates) pairs
    articles = []
    pairs = rss_a[1].items()
    for url, pubdate in pairs:        
        articles += crawl_url(database, url, date=pubdate, depth=depth)
        
    return articles

        
if __name__ == "__main__":
    
    db = Database('test_rss.db')
    db.create_tables()  
    '''
    test_rss1 = rss_feed("http://www.cbc.ca/cmlink/rss-topstories")
    print test_rss1[0]
    for i in test_rss1[1].items():
        print i 
        '''
    print "====time convert====  Tue, 12 Nov 2014 17:58:48 EST"
    isottest = time_convert("Tue, 22 Nov 2014 17:58:48 EST")
    print "Tue, 11 Nov 2014 17:58:48 EST"
    print isottest
    '''
    print "====craw rss===="   
    pairs = test_rss1[1].items()
    for url, pubdate in pairs: 
        print url
        print pubdate
        url = requests.get(url).url
        print url
        
        craw_rss1 = crawl_url(db, url, 
                              date= pubdate,
                              depth=6)
                              
        print craw_rss1
        print len(craw_rss1)
    
    print "====parse_rss===="
    parse_rss1 = parse_rss("http://www.cbc.ca/cmlink/rss-topstories", 2)
    print parse_rss1[0]
    for arti in parse_rss1[1].items():
        print arti   
    print "====parse_end===="
    '''
    db.close()
    os.remove('test_rss.db')
