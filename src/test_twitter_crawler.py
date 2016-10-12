import unittest
from bs4 import BeautifulSoup
from tld.exceptions import TldDomainNotFound, TldBadUrl
from dateutil import parser
from database import Database
from article import Article
from keywords import Keyword
from reference import Reference
from web import crawl_url
from twitter_crawler import *
import requests
import os

class TestTwitterCrawler(unittest.TestCase):
    
    def setUp(self):
        """(TestWebCrawler) -> None
        Set up the database file for testing.
        """
        self.db = Database("testTwitter")
        self.db.create_tables() 
        self.invalid_domain = "ww.gs.ftghd.///sdgjssofsdkfl"
        self.valid_a1 = 'http://www.cnn.com/2014/11/26/us/uva-response-rape-allegatio'+\
        'ns/index.html?hpt=hp_c2'
        self.valid_a2 = "http://www.cnn.com/2014/11/26/opinion/kohn-uva-rape-a"+\
            "llegations/index.html"
        
        
    def tearDown(self):
        """(TestWebCrawler) -> None
        Remove the database test file.
        """
        self.db.close()    
        
    def test_article_to_db_invalid_url(self):
        """
        """
        
        test = article_to_db(self.db, self.invalid_domain)
        self.assertTrue(test == [])
        
    def test_article_to_db_valid_url(self):
        """
        """
        test = article_to_db(self.db, self.valid_a1)
        self.assertTrue(test[0].url == self.valid_a1)  
        
    def test_article_to_db_valid_url_multi(self):
        """
        """
        test = article_to_db(self.db, self.valid_a1)
        test = article_to_db(self.db, self.valid_a2)
        self.assertTrue(test[0].url == self.valid_a2)        
    
    def test_twi_time_convert_invalid_format(self):
        """(TestRSS) -> None
        Test time format converting function with a wrong time format.
        (i.e. not ctime format)
        The expect result should be en empty string.
        """          
        isof = twi_time_convert("Wed, Nov 26 01:45:12 +0000 2014")
        self.assertTrue(isof == '')
    
    def test_twi_time_convert_less_element(self):
        """(TestRSS) -> None
        Test time format converting function with les time element than required.
        (i.e. not ctime format)
        The expect resuld should be en empty string.
        """          
        isof = twi_time_convert("Wed, Nov 26 01:45:12 2014")
        self.assertTrue(isof == '')
    
    def test_twi_time_convert_valid_format(self):
        """(TestRSS) -> None
        Test time format converting function with a valid ctime 
        format string.
        The expect resuld should be a corresponding iso-time format 
        string.
        """         
        isof = twi_time_convert("Wed Nov 26 01:45:12 +0000 2014")
        self.assertTrue(isof == '20141126')     
        
        
        
        
if __name__ == "__main__":
    unittest.main(exit=False)