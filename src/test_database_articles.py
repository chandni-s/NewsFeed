import unittest
from database import Database
from source import Source
from article import Article


class TestDBArticles(unittest.TestCase):

    def setUp(self):
        """(TestDBArticles) -> None
        Set up the database file for testing.
        """
        self.db = Database(":memory:")
        self.db.create_tables()

        # Add a source into the database to add articles to
        self.db.add_source(Source("http://test_source.com"))

    def tearDown(self):
        """(TestDBArticles) -> None
        Remove the database test file.
        """
        self.db.close()

    def test_add_article(self):
        """(TestDBArticles) -> None
        Test add_article to add an article to the database.
        """
        url = "http://test_source.com/add_article.html"
        article = Article(url, "Title", "Date", "Author", "Tags", False)

        # Test that the database adds the article
        self.assertTrue(self.db.add_article(article))

        # Confirm that the article is inside the database
        result = self.db.get_articles()
        self.assertEqual(result.count(), 1)
        result = result.first()
        self.assertEqual(article.url, result.url)
        self.assertEqual(article.title, result.title)
        self.assertEqual(article.date, result.date)
        self.assertEqual(article.author, result.author)
        self.assertEqual(article.tags, result.tags)
        self.assertEqual(article.watched, result.watched)

    def test_add_article_invalid_source_add(self):
        """(TestDBArticle) -> None
        Test add_article when the source is invalid and automatically added
        to the database by add_article.
        """
        source = "veryveryuniquesource.com"
        url = "veryveryuniquesource.com/no_source.html"
        article = Article(url, "Title", "Date", "Author", "Tags", False)

        # Add the article to the database
        self.assertTrue(self.db.add_article(article, True))

        # Confirm that the article is inside the database
        result = self.db.get_articles()
        self.assertEqual(result.count(), 1)

        # Confirm that the article contains the appropriate information
        result = result.first()
        self.assertEqual(result.source_id, 2)

        # Confirm that the new source is inside the database
        result = self.db.get_sources(source)
        self.assertEqual(result.count(), 1)


    def test_add_article_invalid_source(self):
        """TestDBArticle) -> None
        Test add_article when source is invalid and without automatically
        addition of source.
        """
        source = "http://test_sourcea.com"
        url = "http://test_sourcea.com/add_article.html"
        article = Article(url, "Title", "Date", "Author", "Tags", False)

        # Test that the database does not add the article
        self.assertFalse(self.db.add_article(article, False))

    def test_add_article_duplicate_url(self):
        """(TestDBArticles) -> None
        Test add_article when an article with the same url is already inside
        the database.
        """
        source = "http://test_source.com"
        url = "test_source.com/add_article.html"
        article = Article(url, "Title", "Date", "Author", "Tags", False)

        # Add the first article
        self.assertTrue(self.db.add_article(article))
        id = self.db.get_articles(url).first().id

        # Attempt to add the second article with same url
        self.assertTrue(self.db.add_article(article))

        # Confirm that there is one article inside the db and id has incremented
        articles = self.db.get_articles()
        self.assertEqual(articles.count(), 1)
        self.assertEqual(articles.first().id, id + 1)

    def test_add_article_duplicate_url_changes(self):
        """(TestDBArticle) -> None
        Test modify article when the article is there already and changes
        are made to the other fields.
        """
        source = "http://test_source.com"
        url = "http://test_source.com/modify.html"
        article = Article(url, "Title", "Date", "Author", "Tags", False)

        # Add the article to the database
        self.db.add_article(article)

        #Modify the article by adding the same article
        new_article = Article(url, "Title", "Date", "A", "World news", True)
        self.db.add_article(new_article)

        #Confirm the changes that have been made
        result = self.db.get_by_id(Article, 2)
        self.assertEqual(new_article.author, result.author)
        self.assertEqual(new_article.tags, result.tags)

    def test_add_article_twitter(self):
        """(TestDBArticle) -> None
        Test add article when the article belongs to a twitter account
        and the source/account does not exist already.
        """
        url = "twitter.com/cnnnews/1239189451"
        article = Article(url, "Title")

        # Add the article
        self.db.add_article(article)

        # Confirm that the article is there
        result = self.db.get_by_id(Article, 1)
        self.assertEqual(result.url, url)
        self.assertEqual(result.title, "Title")

    def test_add_article_twitter_do_not_add_source(self):
        """(TestDBArticle) -> None
        Test add tweet when the source is not inside of the database already
        but the database does not add the source automatically.
        """
        url = "twitter.com/cnnnews/123123123"
        article = Article(url, "Title")

        # Attempt to add the article
        self.assertFalse(self.db.add_article(article, add_source=False))

        # Confirm that no changes have been made
        self.assertEqual(self.db.get_articles().count(), 0)

    def test_delete(self):
        """(TestDBArticles) -> None
        Test delete_by_id when the article contains the item.
        """
        source = "http://test_source.com"
        url = "http://test_source.com/delete_article.html"
        article = Article(url, "Title", "Date", "Author", "Tags", False)

        self.db.add_article(article)

        # Confirm that the article is inside the database
        id = 1
        self.assertTrue(self.db.get_by_id(Article, id))

        # Remove the article from the database
        self.assertTrue(self.db.delete_by_id(Article, id))

        # Confirm that the article is no longer inside the db
        self.assertFalse(self.db.get_by_id(Article, id))

    def test_delete_article_invalid_id(self):
        """(TestDBArticle) -> None
        Test delete_by_id when the article doesn't contain the item
        """
        id = 1

        # Confirm that the article with id is not inside the db
        self.assertFalse(self.db.get_by_id(Article, id))

        # Attempt to remove the article
        self.assertTrue(self.db.delete_by_id(Article, id))

        # Confrim that nothing has changed
        self.assertFalse(self.db.get_by_id(Article, id))

    def test_get_article(self):
        """TestDBArticle) -> None
        Test get_by_id when the article is inside the db.
        """
        url = "http://test_source.com/get.html"
        art = Article(url, "Title", "Date", "Author", "Tags", False)

        # Add the article into the db
        self.db.add_article(art)

        # Get the article and confirm that it is the one we added.
        result = self.db.get_by_id(Article, 1)
        self.assertTrue(result.url == url)
        self.assertTrue(result.title == "Title")
        self.assertTrue(result.author == "Author")
        self.assertTrue(result.date == "Date")
        self.assertTrue(result.tags == "Tags")
        self.assertTrue(result.watched == False)

    def test_get_article_invalid_id(self):
        '''(TestDBArticle) -> None
        Test get_by_id when id of the article is invalid.
        '''
        self.assertEqual(self.db.get_by_id(Article, 1), None)

    def test_get_articles_empty(self):
        '''(TestDBArticle) -> None
        Test get_Articles when article table is empty.
        '''
        articles = self.db.get_articles()

        # Confirm that there are no articles inside the database
        self.assertEquals(articles.count(), 0)

    def test_get_articles(self):
        '''(TestDBArticle) -> None
        Test get_articles when article table contains articles.
        '''
        source = "http://test_source.com"
        url = "http://test_source.com/get_articles.html"
        art = Article(url, "Title", "Date", "Author", "Tags", False)

        # Add the article into the database
        self.db.add_article(art)

        # Get the articles from the database
        result = self.db.get_articles()

        # Confirm that it is not empty
        self.assertEquals(result.count(), 1)

        # Check the article that we found is the same as the one we added
        result = result.first()
        self.assertTrue(result.id == 1)
        self.assertTrue(result.url == url)
        self.assertTrue(result.title == "Title")
        self.assertTrue(result.author == "Author")
        self.assertTrue(result.date == "Date")
        self.assertTrue(result.tags == "Tags")
        self.assertTrue(result.watched == False)

    def test_get_articles_invalid_url(self):
        '''(TestDBArticle) -> None
        Test get_articles when the url provided doesn't match with any of the
        articles inside the database.
        '''
        source = "http://test_source.com"
        url = "http://test_source.com/get_articles.html"
        art = Article(url, "Title", "Date", "Author", "Tags", False)

        # Add the article into the database
        self.db.add_article(art)

        # Confirm that an invalid query does not return any articles
        new_url = "happy.com/hello.html"
        articles = self.db.get_articles(new_url)
        self.assertEqual(articles.count(), 0)

    def test_get_articles_valid_combination_unique(self):
        """(TestDBArticles) -> None
        Test get_articles when a valid combation of fields are provided and
        only one article matches the search criteria.
        """
        url = "http://test_source.com/get_articles_combo.html"
        url_auth = "http://test_source.com/get_articles_Bob.html"

        art_true = Article(url, "Title", "Date", "Author", "Tags", False)
        art_auth = Article(url_auth, "Title", "Date", "Bob", "Tags", False)

        # Add some articles into the database
        self.db.add_article(art_true)
        self.db.add_article(art_auth)

        # Get the articles from the database
        articles = self.db.get_articles("", "", "Author", "")

        # Confirm that we found art_true
        self.assertEqual(articles.count(), 1)
        result = articles.first()
        self.assertEqual(result.date, art_true.date)
        self.assertEqual(result.author, art_true.author)

    def test_get_articles_valid_combination_many(self):
        """(TestDBArticles) -> None
        Test get_articles when a valid combation of fields are provided and
        some articles matches the search criteria.
        """
        url = "http://test_source.com/get_articles_combo.html"
        url_auth = "http://test_source.com/get_articles_Bob.html"
        url_date = "http://test_source.com/get_articles_2011.html"
        art_true = Article(url, "Title", "2012", "Author", "Tags", False)
        art_auth = Article(url_auth, "Title", "2000", "Bob", "Tags", False)
        art_date = Article(url_date, "Title", "2011", "Author", "Tags", False)

        # Add some articles into the database
        self.db.add_article(art_true)
        self.db.add_article(art_auth)
        self.db.add_article(art_date)

        # Get the articles from the database
        articles = self.db.get_articles("", "", "Author", "", "2011")

        # Confirm that we found two articles
        self.assertEqual(articles.count(), 2)

    def test_get_articles_invalid_combination(self):
        """(TestDBArticles) -> None
        Test get_articles when a combination of fields are provided but
        no article should match the search criteria.
        """
        url = "http://test_source.com/get.html"
        url_date = "http://test_source.com/get_2013.html"
        art_true = Article(url, "Title", "Date", "Author", "Tags", False)
        art_date = Article(url_date, "Title", "2013", "Author", "Tags", False)

        # Add some articles into the database
        self.db.add_article(art_true)
        self.db.add_article(art_date)

        # Attempt to find articles and confirm that none are found
        articles = self.db.get_articles("", "Very unique title")
        self.assertEqual(articles.count(), 0)

if __name__ == "__main__":
    unittest.main(exit=False)
