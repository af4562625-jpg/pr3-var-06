"""Модель книги для системы управления библиотекой (вариант 06)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    isbn: str
    title: str
    author: str
    borrowed_by: str | None = None

    @property
    def available(self) -> bool:
        return self.borrowed_by is None
