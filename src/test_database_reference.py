import unittest
from database import Database
from source import Source
from article import Article
from reference import Reference
import os


class TestDBReferences(unittest.TestCase):

    def setUp(self):
        """(TestDBSources) -> None
        Set up the database file for testing.
        """
        self.db = Database("testsources.db")
        self.db.create_tables()

	#Set up some sources for article and references
	self.db.add_source(Source("http://test_source_1.com"))
	self.db.add_source(Source("http://test_source_2.com"))

	#Add an article to the first test_source
	self.db.add_article(Article("http://test_source_1.com", "T", "A",
	                            "http://test_source_1.com/test_article.html",
	                            "D"))
    def tearDown(self):
        """(TestDBSources) -> None
        Remove the database test file.
        """
        self.db.close()
        os.remove("testsources.db")

    def test_add_reference(self):
        """(TestDBReferences) -> None
        Test add_reference when reference source does exist and there is
        no reference article.
        """
        ref_source = Source("http://test_source_2.com")

        #Add the reference to the database
        self.assertTrue(self.db.add_reference(Reference(1, 2)))

    def test_add_reference_invalid_article(self):
	"""(TestDBReferences) -> None
	Test add_reference when the reference contains the reference article,
	but the database does not contain that article.
	"""
	ref_source = Source("http://test_source_2.com")
	ref_article = 2

	#Attempt to add the reference to the database
	self.assertFalse(self.db.add_reference(Reference(22, 2)))

    def test_add_reference_exists(self):
        '''(TestDBReference) -> None
        Test add_reference when reference is already inside the database
        '''
        self.db.add_source(Source("www.cnn.com"))
	url = "http://test_source.com/add_article.html"
        self.db.add_article(Article(url, "CNNTitle", "12/12/2013",
	                            "CNNAuthor", "Tags", False))

        self.db.add_source(Source("www.asd.ca"))
        self.db.add_reference(Reference(1, 2))
        result = self.db.add_reference(Reference(1, 2))
        self.assertTrue(result == False)

    def test_add_reference_source_dne(self):
        '''(TestDBReference) -> None
        Test add_reference when reference is already inside the database
        '''
        self.db.add_source(Source("www.cnn.com"))
	url = "http://testing.ca/add_article.html"
	self.db.add_article(Article(url, "CNNTitle", "12/12/2013",
			                    "CNNAuthor", "Tags", False))

        self.db.add_reference(Reference(1, 2))
        result = self.db.add_reference(Reference(1, 2))
        self.assertTrue(result == False)

    def test_add_reference_multi(self):
        '''(TestDBReference) -> None
        Test add_reference multiply time into the database
        '''
        self.db.add_source(Source("www.cnn.com"))

        url = "http://cnn.ca/add_article.html"
	self.db.add_article(Article(url, "CNNTitle", "12/12/2013",
			                    "CNNAuthor", "Tags", False))


        self.db.add_source(Source("www.bbc.com"))
        url = "http://bbc.ca/add_article.html"
	self.db.add_article(Article(url, "BCCTitle", "12/5/2013",
			                    "BCCAuthor", "Tags", False))
        a1 = self.db.add_reference(Reference(1, 2))
        a2 = self.db.add_reference(Reference(2, 3))
        self.assertTrue(a1 == True)
        self.assertTrue(a2 == True)

    def test_add_reference_invalid(self):
        '''(TestDBReference) -> None
        Test add_reference when invalid object is given
        '''
	self.assertFalse(self.db.add_reference(Reference(5, 4)))

    def test_add_reference_same_source(self):
        '''(TestDBReference) -> None
        Test add_references when source reference has same source of article.
        It shouldnt be counted in this case.
        '''
        self.db.add_source(Source("http://gah.ca/add_article.html"))
        url = "http://gah.ca/add_article.html"
	self.db.add_article(Article(url, "GahTitle", "5/5/2013",
			                    "GahAuthor", "Tags", False))
        self.db.add_reference(Reference(2, 3))
        self.db.add_reference(Reference(2, 3))
        result = self.db.get_references(1)
        self.assertTrue(result.count() == 0)

    def test_add_reference_same_url(self):
        '''(TestDBReference) -> None
        Test add_references multiple reference have same url but with different
        keyword name. It should only be counted as 1 reference.
        '''
        self.db.add_source(Source("www.gah.com"))
        self.db.add_source(Source("www.blah.com"))
        self.db.add_article(Article("www.gah.com", "GahTitle", "9/9/1999",
	                            "GahAuthor", "tags", False))

        self.db.add_reference(Reference(1, 2))
        self.db.add_reference(Reference(1, 2))
        result = self.db.get_references(1)
        self.assertTrue(result.count() == 1)

    def test_delete_reference_exists(self):
        '''(TestDBReference) -> None
        Test delete_reference when removing a reference that is already
        inside the database.
        '''
        self.db.add_source(Source("www.amc.com"))
        self.db.add_article(Article("www.amc.com", "AMCTitle", "12/12/2013",
	                            "AMCAuthor","tags", False))

        self.db.add_source(Source("www.check.com"))
        self.db.add_reference(Reference(1, 2))
        self.db.delete_by_id(Reference, 1)
        result = self.db.get_references(1)
        self.assertTrue(result.count() == 0)

    def test_delete_reference_non_exists(self):
        '''(TestDBReference) -> None
        Test delete_reference when removing a reference that is not
        inside the database.
        '''
        self.db.add_source(Source("www.cma.com"))
        self.db.add_article(Article("www.cma.com", "CMATitle", "1/1/2013",
	                            "CMAAuthor","tags", False))

        self.db.add_source(Source("www.dsa.com"))
        self.db.add_reference(Reference(1, 2))

        # delete reference that DNE
        self.db.delete_by_id(Reference, 2)
        result = self.db.get_references(1)
        self.assertTrue(result.count() == 1)


    def test_delete_reference_str_id(self):
        '''(TestDBReference) -> None
        Test delete_reference when when giving an str type id.
        '''
        self.db.add_source(Source("www.cma.com"))
        self.db.add_article(Article("www.cma.com", "CMATitle", "1/1/2013",
	                            "CMAAuthor", "tags", False))

        self.db.add_source(Source("www.dsa.com"))
        self.db.add_reference(Reference(1, 2))

        # delete reference that DNE
        result = self.db.delete_by_id(Reference, "2")
        self.assertFalse(result == False)


    def test_get_reference_empty(self):
        '''(TestDBReference) -> None
        Test get_references when reference table is empty.
        '''
        result = self.db.get_references(9)
        self.assertTrue(result.first() == None)

    def test_get_reference_str_id(self):
        '''(TestDBReference) -> None
        Test get_references with a str type id input.
        '''
        self.db.add_source(Source("www.gah.com"))
        self.db.add_article(Article("www.gah.com", "GAHTitle", "5/4/2013",
	                            "GAHAuthor", "tags", False))

        self.db.add_source(Source("www.coding.com"))
        self.db.add_reference(Reference(1, 2))
        result = self.db.get_references('1')
        self.assertTrue(result.count() == 1)
	self.assertTrue(result.first().source_id == 2)

    def test_get_reference_exists(self):
        '''(TestDBReference) -> None
        Test get_references when reference table has it.
        '''
        self.db.add_source(Source("www.abc.com"))
        self.db.add_article(Article("www.abc.com", "ABCTitle", "9/9/1999",
	                            "ABCAuthor", "tags", False ))

        self.db.add_source(Source("www.coding.com"))
        self.db.add_reference(Reference(1, 3))
        result = self.db.get_references(1)
        self.assertTrue(result.count() == 1)
	self.assertTrue(result.first().source_id == 3)


    def test_get_reference_invalid(self):
        '''(TestDBReference) -> None
        Test get_references with invalid id input(id out of range).
        '''
        self.db.add_source(Source("www.apple.com"))
        self.db.add_article(Article("www.apple.com", "ApTitle", "4/6/2011",
	                            "AppleAuthor", "tags", False))

        self.db.add_source(Source("www.nuts.com"))
        self.db.add_reference(Reference(1, 3))
        try:
            result = self.db.get_references(4)
        except:
            self.assertTrue(True)

    def test_get_reference_many(self):
        '''(TestDBReference) -> None
        Test get_references with input id article has many reference.
        '''
        self.db.add_source(Source("www.xyz.com"))
        self.db.add_source(Source("www.lmn.com"))
        self.db.add_article(Article("www.lmn.com", "LemonTitle",
	                            "5/2/1990", "LemonAuthor", "tags",
	                            False))

        self.db.add_source(Source("www.wow.com"))
        self.db.add_reference(Reference(1, 3))
        self.db.add_reference(Reference(1, 2))
        result = self.db.get_references(1)
        self.assertTrue(result.count() == 2)

if __name__ == "__main__":
    unittest.main(exit=False)
