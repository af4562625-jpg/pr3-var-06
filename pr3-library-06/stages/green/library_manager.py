"""TDD / GREEN: первая рабочая версия без выделенных служебных методов."""
from dataclasses import replace
from models import Book


class LibraryManager:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    def add_book(self, isbn: str, title: str, author: str) -> Book:
        if not isinstance(isbn, str) or not isbn.strip():
            raise ValueError("ISBN должен быть непустой строкой")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Название должен быть непустой строкой")
        if not isinstance(author, str) or not author.strip():
            raise ValueError("Автор должен быть непустой строкой")
        isbn, title, author = isbn.strip(), title.strip(), author.strip()
        if isbn in self._books:
            raise ValueError("Книга с таким ISBN уже существует")
        book = Book(isbn, title, author)
        self._books[isbn] = book
        return book

    def find_book(self, query: str) -> Book | None:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Поисковый запрос должен быть непустой строкой")
        query = query.strip()
        if query in self._books:
            return self._books[query]
        q = query.casefold()
        for book in self.list_books():
            if q in book.title.casefold():
                return book
        return None

    def search_books(self, query: str) -> tuple[Book, ...]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Поисковый запрос должен быть непустой строкой")
        query = query.strip()
        if query in self._books:
            return (self._books[query],)
        q = query.casefold()
        return tuple(b for b in self.list_books() if q in b.title.casefold())

    def list_books(self) -> tuple[Book, ...]:
        return tuple(self._books[k] for k in sorted(self._books))

    def borrow_book(self, isbn: str, reader_id: str) -> Book:
        if not isinstance(isbn, str) or not isbn.strip():
            raise ValueError("ISBN должен быть непустой строкой")
        isbn = isbn.strip()
        if isbn not in self._books:
            raise KeyError("Книга не найдена")
        if not isinstance(reader_id, str) or not reader_id.strip():
            raise ValueError("ID читателя должен быть непустой строкой")
        book = self._books[isbn]
        if not book.available:
            raise ValueError("Книга уже выдана")
        updated = replace(book, borrowed_by=reader_id.strip())
        self._books[isbn] = updated
        return updated

    def return_book(self, isbn: str) -> Book:
        if not isinstance(isbn, str) or not isbn.strip():
            raise ValueError("ISBN должен быть непустой строкой")
        isbn = isbn.strip()
        if isbn not in self._books:
            raise KeyError("Книга не найдена")
        book = self._books[isbn]
        if book.available:
            raise ValueError("Книга не была выдана")
        updated = replace(book, borrowed_by=None)
        self._books[isbn] = updated
        return updated
