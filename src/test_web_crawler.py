import unittest
from bs4 import BeautifulSoup
from tld.exceptions import TldDomainNotFound, TldBadUrl
from dateutil import parser
from database import Database
from article import Article
from keywords import Keyword
from reference import Reference
from web import crawl_url
import requests
import os

class TestWebCrawler(unittest.TestCase):

    def setUp(self):
        """(TestWebCrawler) -> None
        Set up the database file for testing.
        """
        self.db = Database("testCrawler")
        self.db.create_tables()
        self.result_valid_url = ['Ferguson mayor: Protests possible over grand j'
                                 'ury - CNN.com', 'Michael Brown, teen shot by'
                                 'police, days before college - CNN.com',
                            'dont-shoot-coalition', 'What happened when Michael B'
                            'rown met Officer Darren Wilson - CNN.com', 'Police: '
                            'Ferguson no-fly zone not meant to ban media - CNN.co'
                            'm', 'Ferguson Mayor plans for grand jury decisio'
                            'n | FOX2now.com', 'Ferguson: The signal it sends abo'
                            'ut America (Opinion) - CNN.com', 'Paul Callan (@Pau'
                            'lCallan) | Twitter', 'Mo Ivory, Esq. (@moivory) | Tw'
                            'itter', 'Ferguson: Michael Brown case rests on facts'
                            ' (Opinion) - CNN.com']
    def tearDown(self):
        """(TestWebCrawler) -> None
        Remove the database test file.
        """
        self.db.close()

    def testInvalidUrl(self):
        '''(TestDBArticles) -> None
        Test crawling an invalid URL
        '''
        craw_test = crawl_url(self.db, 'htasdshsfsdf.yttml', depth=2)
        self.assertTrue(craw_test == [])

    def testValidUrl_zero_depth(self):
        '''(TestDBArticles) -> None
        Test crawling an article with valid URL but depth of 0 - should return
        empty
        '''
        craw_test = crawl_url(self.db, 'http://www.cnn.com/2014/11/06/us/fergu'
                              'son-rules-protests/index.html', depth=0)
        self.assertTrue(craw_test == [])

    def testValidUrl_one_depth(self):
        '''(TestDBArticles) -> None
        Test crawling an article with valid url and depth of 1
        - should return a single article
        '''
        single_arti = 'Ferguson mayor: Protests possible over grand jury - CNN.com'
        craw_test = crawl_url(self.db, 'http://www.cnn.com/2014/11/06/us/fergu'
                              'son-rules-protests/index.html', depth=1)
        self.assertTrue(len(craw_test)<2)
        if craw_test != []:
            self.assertTrue(craw_test[0].title == single_arti)   

    def testValidUrl_multi_depth(self):
        '''(TestDBArticles) -> None
        Test crawling an article with valid url and depth > 1
        should return multiple articles
        '''
        craw_test = crawl_url(self.db, 'http://www.cnn.com/2014/11/06/us/fergu'
                              'son-rules-protests/index.html', depth=2)
        self.assertTrue(len(craw_test)<11)
        for article in craw_test:
            self.assertTrue(article.title in self.result_valid_url)
     

if __name__ == "__main__":
    unittest.main(exit=False)
