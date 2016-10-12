import unittest
from database import Database
from source import Source


class TestDBSources(unittest.TestCase):

    def setUp(self):
        """(TestDBSources) -> None
        Set up a temporary database file for testing.
        """
        # Setup the database, and create the tables to use.
        self.db = Database(":memory:")
        self.db.create_tables()

    def tearDown(self):
        """(TestDBSources) -> None
        Close the connection to the temporary database test file and remove it.
        """
        # Close the connection to the database.
        self.db.close()

    def test_add_source(self):
        """(TestDBSources) -> None
        Test adding a new source to the database.
        """
        name = 'test.com'

        # Add the source into the database
        self.assertTrue(self.db.add_source(Source(name)))

        # Confirm that the source has been added
        self.assertTrue(self.db.get_sources(name).count() == 1)

    def test_add_source_duplicate_name(self):
        """(TestDBSources) -> None
        Adds a duplicate source to the database.
        """
        name = "duplicate_source.com"

        # Add the source to the database.
        self.assertTrue(self.db.add_source(Source(name)))
        id = self.db.get_sources(name).first().id

        # Attempt to add the same source and confirm that the id has
        # incremented by 1.
        self.assertTrue(self.db.add_source(Source(name)))
        new_id = self.db.get_sources(name).first().id
        self.assertTrue(id + 1 == new_id)

    def test_add_source_many(self):
        """(TestDBSources) -> None
        Adds many sources to the database.
        """
        # Add 1000 different sources.
        for i in range(0, 1000):
            self.assertTrue(self.db.add_source(Source("%d.com" % i)))

        # Confirm that there are indeed 1000
        self.assertTrue(self.db.get_sources().count())

    def test_add_source_duplicates_many(self):
        """(TestDBSources) -> None
        Test adding duplicate sources when there are other sources inside.
        """
        name = "cnn.com"

        # Add some sources into the database
        self.db.add_source(Source(name))
        self.db.add_source(Source("ABC.com"))
        self.db.add_source(Source("can.com"))
        count = 3

        # Add the same source again and check that the id has changed
        self.db.add_source(Source(name))
        source = self.db.get_sources(name).first()

        self.assertEquals(source.id, count + 1)

    def test_add_source_empty_name(self):
        """(TestDBSources) -> None
        Test that empty sources cannot be added to the db.
        """
        # Adding an empty source should result in failure.
        self.assertFalse(self.db.add_source(Source('')))

        # Confirm that there are no sources inside the database
        self.assertEqual(self.db.get_sources().count(), 0)

    def test_add_website_startswith_http(self):
        """(TestDBSources) -> None
        Test that the database will add a source called http://twitter.com
        """
        name = "http://twitter.com"

        # Add the source
        self.assertTrue(self.db.add_source(Source(name)))

        # Confirm that the source has url "twitter.com"
        self.assertEqual(self.db.get_by_id(Source, 1).url, "twitter.com")

    def test_add_website_startswith_http_www(self):
        """(TestDBSources) -> None
        Test that the database will add a source called http://www.twitter.com
        """
        name = "http://www.twitter.com"

        # Add source
        self.assertTrue(self.db.add_source(Source(name)))

        # Confirm that the source has url "twitter.com"
        self.assertEqual(self.db.get_by_id(Source, 1).url, "twitter.com")

    def test_add_website_startswith_www(self):
        """(TestDBSources) -> None
        Test that the database will ad a source starting with www.
        """
        name = "www.twitter.com"

        # Add the source into the database
        self.assertTrue(self.db.add_source(Source(name)))

        # Confirm that the source has name twitter.com
        self.assertEqual(self.db.get_by_id(Source, 1).url, "twitter.com")

    def test_twitter_add_account(self):
        """(TestDBSources) -> None
        Test that the database will add a source to a twitter account.
        """
        name = "www.twitter.com/cnn/"

        # Add the source into the database
        self.assertTrue(self.db.add_source(Source(name)))

        # Confirm that the source has url twitter.com/cnn
        self.assertEqual(self.db.get_by_id(Source, 1).url, "twitter.com/cnn")

    def test_get_source_by_id(self):
        """(TestDBSources) -> None
        Test get_by_id with a source returns the correct source.
        """
        # Add the source
        self.assertTrue(self.db.add_source(Source('test.com')))

        # Find the source in the database.
        id = self.db.get_sources(url='test.com').first().id

        # Get the source by id.
        source = self.db.get_by_id(Source, id)
        self.assertIsNotNone(source)

        # Check that the correct source was returned
        self.assertTrue(source.url == "test.com")

    def test_get_source_by_invalid_id(self):
        """(TestDBSources) -> None
        Test get_by_id with a source and an invalid id.
        """
        self.assertIsNone(self.db.get_by_id(Source, -1))

    def test_get_sources_empty(self):
        """(TestDBSources) -> None
        Test get_sources when there are no sources inside the database.
        """
        # Generate a query without any filters.
        query = self.db.get_sources()

        # Test the query's results.
        self.assertEqual(query.count(), 0)
        self.assertListEqual(query.all(), [])
        self.assertListEqual(query.subset(), [])

    def test_get_sources_single(self):
        """(TestDBSources) -> None
        Test get_sources to find a single source and there is only one
        source in the database.
        """
        name = "apple.com"

        # Add the source into the database
        self.db.add_source(Source(name))

        # Get the query with the filter name
        query = self.db.get_sources(name)

        # Confirm that we have found the correct one
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().url, name)

    def test_get_sources_similar_names(self):
        """(TestDBSources) -> None
        Test get_sources to find a single source when there are many sources
        that match the filter.
        """
        name = "bob.com"

        # Add sources into the database
        self.db.add_source(Source(name))
        self.db.add_source(Source("bobby.com"))
        self.db.add_source(Source("bobbing.com"))

        # Get the query with the filter name
        query = self.db.get_sources(name)

        # Confirm that we have only found oen
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().url, name)

    def test_get_sources_invalid_query(self):
        """(TestDBSources) -> None
        Tests getting a list of sources with an invalid filter query.
        """
        # Add some sources into the database
        self.db.add_source(Source("cnn.com"))
        self.db.add_source(Source("abc.com"))
        self.db.add_source(Source("app.com"))

        # Get the query with a filter that doesn't match
        query = self.db.get_sources("cn")

        # Confirm that there are no sources that match
        self.assertEqual(query.count(), 0)

    def test_get_sources_nonempty_additions(self):
        """(TestDBSources) -> None
        Tests get_sources when repeatedly adding new items and overwriting
        existing ones.
        """
        # Add sources to the database
        for i in range(0, 25):
            for j in range(0, i):
                # Add sources to the database.
                self.assertTrue(self.db.add_source(Source('%d.com' % i)))

            # Generate a query without any filters.
            query = self.db.get_sources()
            all = query.all()

            # Test the query's results.
            self.assertEqual(query.count(), i)
            self.assertEqual(len(all), i)
            self.assertEqual(len(query.subset()), min(i, 10))

    def test_delete_source(self):
        """(TestDBSources) -> None
        Remove a source that is inside the database.
        """
        name = "test_delete_source.com"

        #Add the source to the database
        self.db.add_source(Source(name))

        id = self.db.get_sources(name).first().id

        #Remove the source
        self.assertTrue(self.db.delete_by_id(Source, id))

        #Confirm that the source is not in the database
        self.assertFalse(self.db.get_by_id(Source, id))

    def test_delete_source_other_sources(self):
        """(TestDBSources) -> None
        Remove a source from the database when there are other sources in there.
        """
        name = "test_delete_source_many.com"

        # Adds sources into the database
        self.db.add_source(Source("Bob.com"))
        self.db.add_source(Source(name))
        self.db.add_source(Source("CNN.com"))
        self.db.add_source(Source("ebay.com"))

        # Remove the source
        self.assertTrue(self.db.delete_by_id(Source, 2))

        # Confirm that the source is no longer there
        self.assertEqual(self.db.get_sources(name).count(), 0)

        # Confirm that the other sources are still there
        self.assertEqual(self.db.get_sources().count(), 3)

    def test_delete_source_multiple(self):
        """(TestDBSources) -> None
        Remove multiple sources from the db.
        """
        name_cnn = "cnn.com"
        name_abc = "abc.com"

        # Adds sources into the database
        self.db.add_source(Source(name_cnn))
        self.db.add_source(Source(name_abc))
        self.db.add_source(Source("asd.com"))
        self.db.add_source(Source("Others.com"))

        # Remove two sources from the database
        self.assertTrue(self.db.delete_by_id(Source, 1))
        self.assertTrue(self.db.delete_by_id(Source, 2))

        # Confirm that they are no longer there
        self.assertEqual(self.db.get_sources(name_cnn).count(), 0)
        self.assertEqual(self.db.get_sources(name_abc).count(), 0)

        # Confirm that the other two are still inside the database
        self.assertEqual(self.db.get_sources().count(), 2)

    def test_delete_source_invalid_id(self):
        """(TestDBSources) -> None
        Attempt to remove a source that is not inside the database.
        """
        id = 1

        # Confirm that the source at id does not exist
        self.assertFalse(self.db.get_by_id(Source, id))

        # Attempt to remove a source from the database - Delete returns true
        self.assertTrue(self.db.delete_by_id(Source, id))

        # Confirm that nothing has changed at id
        self.assertFalse(self.db.get_by_id(Source, id))

if __name__ == '__main__':
    unittest.main(exit=False)
