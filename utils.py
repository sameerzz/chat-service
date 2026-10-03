
books = {
    101: {
        "id": 101,
        "title": "Atomic Habits",
        "author": "James Clear"
    },

    102: {
        "id": 102,
        "title": "The Power of Habit",
        "author": "Charles Duhigg"
    }
}


def get_book_details(book_id: int):
    return books.get(book_id)


def add_book_func(book: dict):
    books[book["id"]] = book
    return book