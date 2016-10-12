import unittest
from database import Database
from source import Source
from article import Article
from keywords import Keyword
import os


class TestDBKeywords(unittest.TestCase):

    def setUp(self):
        """(TestDBKeywords) -> None
        Set up the database file for testing.
        """
        self.db = Database("testsources.db")
        self.db.create_tables()

    def tearDown(self):
        """(TestDBKeywords) -> None
        Remove the database test file.
        """
        self.db.close()
        os.remove("testsources.db")
        

    # Testing add functions
    def test_add_keyword_unique(self):
        """(TestDBKeywords) -> None
        Test adding a keyword that is not inside the database already.
        """
        self.db.add_source(Source("www.cnn.com"))
        self.db.add_keyword(Keyword(1, "Manager"))
        result = self.db.get_keywords(1)
        self.assertTrue(result.count() == 1)
        self.assertTrue(result.first().name == "Manager")

    def test_add_keyword_exists_already(self):
        """(TestDBKeywords) -> None
        Test adding a keyword that is already inside the database.
        """
        self.db.add_source(Source("www.cnn.com"))
        self.db.add_keyword(Keyword(1, "Manager"))
        result = self.db.add_keyword(Keyword(1, "Manager"))
        self.assertTrue(result == True)

    def test_add_multiple_keywords(self):
        """(TestDBKeywords) -> None
        Test add keyword multiple times in a row and with multiple sources.
        """
        self.db.add_source(Source("www.cnn.com"))
        self.db.add_source(Source("www.BBC.com"))
        self.db.add_keyword(Keyword(1, "CNNN"))
        self.db.add_keyword(Keyword(2, "BB"))
        result = self.db.get_keywords(1)
        result_a = self.db.get_keywords(2)
        self.assertTrue(result.count() == 1)
        self.assertTrue(result_a.count() == 1)

    def test_add_keyword_invalid(self):
        """(TestDBKeywords) -> None
        Test add_keyword when the source doesn't exist.
        """
        result = self.db.add_keyword(Keyword(1, "CNN"))
        self.assertTrue(result == False)

    # delete keyword
    def test_delete_keyword_empty(self):
        """(TestDBKeywords) -> None
        Test delete_keyword when the table is empty.
        """
        result = self.db.delete_by_id(Keyword, 1)
        result = self.db.get_keywords(1)
        self.assertTrue(result.count() == 0)

    def test_delete_keyword_notempty_exists(self):
        """(TestDBKeywords) -> None
        Test delete_keyword when the table is not empty and the keyword exists.
        """
        self.db.add_source(Source("bbc.com"))
        self.db.add_keyword(Keyword(1, "asd"))
        self.db.delete_by_id(Keyword, 1)
        result = self.db.get_keywords(1)
        self.assertTrue(result.count() == 0)

    def test_delete_keyword_notempty_not_exists(self):
        """(TestDBKeywords) -> None
        Test delete_keyword when the table contains a keyword to source x, but
        attempts to delete keyword that isn't there.
        """
        self.db.add_source(Source("www.abc.com"))
        self.db.add_keyword(Keyword(1, "asd"))
        self.db.delete_by_id(Keyword, 2)
        result = self.db.get_keywords(1)
        self.assertTrue(result.count() == 1)

    # get keywords
    def test_get_keywords_empty(self):
        """(TestDBKeywords) -> None
        Test get_keywords when the tables are empty.
        """
        result = self.db.get_keywords(1)
        self.assertTrue(result.count() == 0)

    def test_get_keywords_notexists(self):
        """(TestDBKeywords) -> None
        Test get_keywords when the table does not contain the source for which
        it wants to get keywords from.
        """
        self.db.add_source(Source("www.al.com"))
        self.db.add_keyword(Keyword(1, "basd"))
        result = self.db.get_keywords(2)
        self.assertTrue(result.count() == 0)

    def test_get_keywords_exist(self):
        """(TestDBKeywords) -> None
        Test get_keywords when the table does contain
        """
        self.db.add_source(Source("www.abc.com"))
        self.db.add_keyword(Keyword(1, "basd"))
        result = self.db.get_keywords(1)
        self.assertTrue(result.first().name == 'basd')


    def test_add_keyword(self):
        '''(TestDBKeywords) -> None
        Test adding a keywords which is already exist in keyword table.
        '''
        self.db.add_source(Source("www.cnn.com"))
        self.db.add_keyword(Keyword(1, "basd"))
        result = self.db.add_keyword(Keyword(1, "basd"))
        self.assertTrue(result)

    def test_remove_keyword(self):
        '''(TestDBKeywords) -> None
        Test removing a keywords which is already exist in keyword table.
        '''
        self.db.add_source(Source("www.bbc.com"))
        a1 = self.db.add_keyword(Keyword(1, "basd"))
        self.assertTrue(a1)
        self.db.delete_by_id(Keyword, 1)
        a2 = self.db.add_keyword(Keyword(1, "basd"))
        self.assertTrue(a2)


if __name__ == "__main__":
    unittest.main(exit=False)
