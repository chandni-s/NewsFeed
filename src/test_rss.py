import unittest
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
from rss import *

class TestRSS(unittest.TestCase):
    
    def setUp(self):
        """(TestRSS) -> None
        Set up the database file for testing.
        """        
        self.db = Database('test_rss.db')
        self.db.create_tables() 
    
    def tearDown(self):
        """(TestRSS) -> None
        Remove the database test file.
        """           
        self.db.close()
        os.remove('test_rss.db')
        
    def test_invalid_RSS(self):
        """(TestRSS) -> None
        Test RSS feed analyzing function with an invalid RSS feed.
        The expect resuld should be 0 feed count.
        """
        rss_test = rss_feed("http://wwwerdfdstories")
        self.assertTrue(rss_test[0] == 0)
        self.assertTrue(rss_test[1] == {})
       
            
    def test_valid_RSS(self):
        """(TestRSS) -> None
        Test RSS feed analyzing function with a valid RSS feed.
        The expect resuld should be 15 feeds cound(specific for CBC),
        and a dictionary that contains all the urls and correct 
        publish date.
        """        
        rss_test = rss_feed("http://www.cbc.ca/cmlink/rss-topstories")
        self.assertTrue(rss_test[0] == 15)
        if rss_test[1] != {}:
            for url in rss_test[1].keys():
                self.assertTrue(url.startswith("http://www.cbc.ca"))
                
    def test_RSS_invalid_url(self):
        """(TestRSS) -> None
        Test RSS feed analyzing function with an valid RSS but invalid url result.
        """
        rss_test = rss_feed("http://www.cbc.ca/cmlink/rss-topstories")
        self.assertTrue(rss_test[0] == 15)
        if rss_test[1] != {}:
            for url in rss_test[1].keys():
                self.assertFalse(url.startswith("cbc.ca"))

    def test_RSS_invalid_total(self):
        """(TestRSS) -> None
        Test RSS feed analyzing function with an valid RSS but invalid total.
        """
        rss_test = rss_feed("http://www.cbc.ca/cmlink/rss-topstories")
        self.assertFalse(rss_test[0] == 4)
        
        
    def test_invalid_parse_rss(self):
        """(TestRSS) -> None
        Test RSS feed analyzing function with an invalid RSS feed.
        The expect resuld should be 0 feed count.
        """
        rss_test = parse_rss(self.db, "http://wwwerdfdstories")
        self.assertTrue(rss_test == [])

       
            
    def test_parse_rss_cbc(self):
        """(TestRSS) -> None
        Test parse_rss with valid CBC RSS feed, all the article title should 
        starts with "http://www.cbc.ca"
        """        
        rss_test = parse_rss(self.db, "http://www.cbc.ca/cmlink/rss-topstories")  
        self.assertTrue(rss_test[0].url.startswith("http://www.cbc.ca"))
        
                
    def test_parse_rss_nytimes(self):
        """(TestRSS) -> None
       Test parse_rss with valid New York Times RSS feed, all the article 
       title should starts with "http://rss.nytimes.com"
        """
        rss_test = parse_rss(self.db, 
                    "http://rss.nytimes.com/services/xml/rss/nyt/Business.xml")  
        self.assertTrue(rss_test[0].url.startswith("http://rss.nytimes.com"))
        

    def test_parse_rss_cnn(self):
        """(TestRSS) -> None
        Test parse_rss with valid CNN RSS feed, all the article title should 
        starts with "http://rss.cnn.com"
        """
        rss_test = parse_rss(self.db, "http://rss.cnn.com/rss/cnn_us.rss")

        self.assertTrue(rss_test[0].url.startswith("http://rss.cnn.com"))
   
               
    def test_time_convert_valid_format(self):
        """(TestRSS) -> None
        Test time format converting function with a valid ctime 
        format string.
        The expect resuld should be a corresponding iso-time format 
        string.
        """         
        isof = time_convert("Tue, 22 Nov 2014 17:58:48 EST")
        self.assertTrue(isof == '2014-11-23')    
                
    def test_time_convert_date_invalid_month(self):
        """(TestRSS) -> None
        Test time format converting function with a wrong date format.
        (i.e. not ctime format)
        The expect result should be en empty string.
        """          
        isof = time_convert("Tue, 11 Nooov 2014 17:58:48 EST")
        self.assertTrue(isof == '') 
        
    def test_time_convert_invalid_result(self):
        '''(TestRSS) -> None
        Test time format converting function with right time format but
        wrong result
        '''
        isof = time_convert("Tue 11 Nov 2013 17:58:48 EST")
        self.assertFalse(isof == '11-2014-11')
        
    def test_time_convert_invalid_time_format(self):
        '''(TestRSS) -> None
        Test time format converting function with wrong time format
        '''
        isof = time_convert("Mon 11 Nov 2014 177:588:48 EST")
        self.assertTrue(isof == '')
    
if __name__=='__main__':
    unittest.main(exit=False)