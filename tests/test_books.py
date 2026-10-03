import copy
import unittest

import utils


class BookCatalogTests(unittest.TestCase):
    def setUp(self):
        original = copy.deepcopy(utils.books)
        self.addCleanup(self.restore_books, original)

    @staticmethod
    def restore_books(original):
        utils.books.clear()
        utils.books.update(original)

    def test_find_existing_book(self):
        self.assertEqual(utils.get_book_details(101)["title"], "Atomic Habits")

    def test_unknown_book_returns_none(self):
        self.assertIsNone(utils.get_book_details(-1))

    def test_added_book_can_be_retrieved(self):
        book = {"id": 999, "title": "Clean Code", "author": "Robert C. Martin"}
        utils.add_book_func(book)
        self.assertEqual(utils.get_book_details(999), book)

    def test_adding_book_preserves_existing_books(self):
        existing = copy.deepcopy(utils.get_book_details(101))
        utils.add_book_func({"id": 999, "title": "New book", "author": "Author"})
        self.assertEqual(utils.get_book_details(101), existing)


if __name__ == "__main__":
    unittest.main()
