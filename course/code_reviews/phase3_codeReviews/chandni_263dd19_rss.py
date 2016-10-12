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
    
    # Get totle count of all updated articles of given RSS feed.
    total = len(d['entries'])
    # Create dictionary for return data.
    updates = dict()
    
    #Loop all the articles to get urls and publish times.
    for index, item in enumerate(d['entries']):
        # Convert publish time from ctime format to iso-time format.
        a_time = time_convert(item.published)
        # Set article url ad dictionary key, with publish date as value. 
        updates[str(item.link)] = a_time
        
    return [total, updates]


def time_convert(timestr):
    """(str) -> str
    Convert time str from ctime format to isoformat,
    i.e. Tue, 11 Nov 2014 17:58:48 EST -> 2014-11-11
    
    Return the given time str in iso-time format.
    """
    # Analyse given time str to seperate elements.
    struct_time = time.strptime(timestr, "%a, %d %b %Y %H:%M:%S %Z")
    # Convert given time bu secend unit.
    t = time.mktime(struct_time) 
    # Re-construct time to isotime format.
    isot = time.strftime("%Y-%m-%d", time.gmtime(t))
    
    return isot


def parse_rss(feed, level=1,):
    """(str, int) -> list(int, dict)
    Get all the updated article links in the RSS feed. 
    Find the reference inside all the articles recursively(set by "level" depth), 
    and add the references into database.
    
    Return the total count of updated articles, and a dictionary with 
    (key: value)<->(aticle_link: publish_date in isotime format).
    """
    # Get the updates article count, and article urls and publish dates.
    rss_a = rss_feed(feed)
    # Get all (article urls, publish dates) pairs
    pairs = rss_a[1].items()
    
    # Loop all articles for reference searching.
    for url, pubdate in pairs:        
        craw_rss = crawl_url(db, url, date= pubdate, depth=level)
        # Add for testing, will detele later
        print craw_rss
        print len(craw_rss) 
    return rss_a
    
        
if __name__ == "__main__":
    
    db = Database('test_craw.db')
    db.create_tables()  
    '''
    test_rss1 = rss_feed("http://www.cbc.ca/cmlink/rss-topstories")
    print test_rss1[0]
    for i in test_rss1[1].items():
        print i 
    print "====time convert===="
    isottest = time_convert("Tue, 12 Nov 2014 17:58:48 EST")
    print "Tue, 11 Nov 2014 17:58:48 EST"
    print isottest
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
    '''
    print "====parse_rss===="
    parse_rss1 = parse_rss("http://www.cbc.ca/cmlink/rss-topstories", 2)
    print parse_rss1[0]
    for arti in parse_rss1[1].items():
        print arti   
    print "====parse_end===="
    
    db.close()
    os.remove('test_craw.db')    
   
    
    "http://www.cbc.ca/cmlink/rss-topstories"
    "http://rss.cnn.com/rss/cnn_topstories.rss"
    "http://rss.cnn.com/rss/cnn_topstories.rss"
    