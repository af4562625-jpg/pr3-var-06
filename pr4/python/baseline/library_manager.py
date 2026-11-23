"""Финальная версия: библиотека с проверяемой бизнес-логикой."""
from dataclasses import replace
from models import Book


class LibraryManager:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    @staticmethod
    def _required_string(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} должен быть непустой строкой")
        return value.strip()

    def _require_book(self, isbn: str) -> Book:
        key = self._required_string(isbn, "ISBN")
        try:
            return self._books[key]
        except KeyError:
            raise KeyError("Книга не найдена") from None

    def add_book(self, isbn: str, title: str, author: str) -> Book:
        key = self._required_string(isbn, "ISBN")
        title = self._required_string(title, "Название")
        author = self._required_string(author, "Автор")
        if key in self._books:
            raise ValueError("Книга с таким ISBN уже существует")
        book = Book(key, title, author)
        self._books[key] = book
        return book

    def find_book(self, query: str) -> Book | None:
        """Поиск точного ISBN, иначе первой книги по фрагменту названия."""
        key = self._required_string(query, "Поисковый запрос")
        if key in self._books:
            return self._books[key]
        matches = self.search_books(key)
        return matches[0] if matches else None

    def search_books(self, query: str) -> tuple[Book, ...]:
        """Все совпадения по ISBN или по названию; сортировка по ISBN."""
        key = self._required_string(query, "Поисковый запрос")
        if key in self._books:
            return (self._books[key],)
        normalized = key.casefold()
        return tuple(b for b in self.list_books() if normalized in b.title.casefold())

    def list_books(self) -> tuple[Book, ...]:
        return tuple(self._books[key] for key in sorted(self._books))

    def borrow_book(self, isbn: str, reader_id: str) -> Book:
        book = self._require_book(isbn)
        reader = self._required_string(reader_id, "ID читателя")
        if not book.available:
            raise ValueError("Книга уже выдана")
        updated = replace(book, borrowed_by=reader)
        self._books[book.isbn] = updated
        return updated

    def return_book(self, isbn: str) -> Book:
        book = self._require_book(isbn)
        if book.available:
            raise ValueError("Книга не была выдана")
        updated = replace(book, borrowed_by=None)
        self._books[book.isbn] = updated
        return updated
