"""TDD / RED: интерфейс объявлен, реализация отсутствует."""
from models import Book


class LibraryManager:
    def __init__(self) -> None:
        pass

    def add_book(self, isbn: str, title: str, author: str) -> Book:
        raise NotImplementedError("Этап RED: add_book не реализован")

    def find_book(self, query: str) -> Book | None:
        raise NotImplementedError("Этап RED: find_book не реализован")

    def search_books(self, query: str) -> tuple[Book, ...]:
        raise NotImplementedError("Этап RED: search_books не реализован")

    def list_books(self) -> tuple[Book, ...]:
        raise NotImplementedError("Этап RED: list_books не реализован")

    def borrow_book(self, isbn: str, reader_id: str) -> Book:
        raise NotImplementedError("Этап RED: borrow_book не реализован")

    def return_book(self, isbn: str) -> Book:
        raise NotImplementedError("Этап RED: return_book не реализован")
