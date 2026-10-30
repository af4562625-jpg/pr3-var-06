"""ATDD: пять критериев приёмки из отчёта по варианту 06."""
import pytest


def test_ac01_add_and_find(library):
    library.add_book("A1", "Мастер и Маргарита", "Булгаков")
    book = library.find_book("A1")
    assert (book.title, book.author, book.available) == ("Мастер и Маргарита", "Булгаков", True)


def test_ac02_borrow_and_return(library):
    library.add_book("A1", "Мастер", "Булгаков")
    borrowed = library.borrow_book("A1", "R1")
    assert (borrowed.available, borrowed.borrowed_by) == (False, "R1")
    returned = library.return_book("A1")
    assert (returned.available, returned.borrowed_by) == (True, None)


def test_ac03_duplicate_preserves_original(library):
    original = library.add_book("A1", "Оригинал", "Автор")
    with pytest.raises(ValueError, match="уже существует"):
        library.add_book("A1", "Подмена", "Автор2")
    assert library.list_books() == (original,)


def test_ac04_second_borrow_preserves_first_reader(library):
    library.add_book("A1", "Книга", "Автор")
    library.borrow_book("A1", "R1")
    before = library.list_books()
    with pytest.raises(ValueError, match="Книга уже выдана"):
        library.borrow_book("A1", "R2")
    assert library.list_books() == before


def test_ac05_unknown_book_does_not_change_catalog(library):
    library.add_book("A1", "Книга", "Автор")
    before = library.list_books()
    with pytest.raises(KeyError, match="Книга не найдена"):
        library.borrow_book("X1", "R1")
    with pytest.raises(KeyError, match="Книга не найдена"):
        library.return_book("X1")
    assert library.list_books() == before
