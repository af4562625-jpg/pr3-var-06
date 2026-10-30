"""TDD: тесты для функциональности и граничных условий."""
from dataclasses import FrozenInstanceError
import pytest


def add_sample(library, isbn="A1", title="Мастер и Маргарита", author="Булгаков"):
    return library.add_book(isbn, title, author)


def test_empty_catalog(library):
    assert library.list_books() == ()


def test_add_book(library):
    book = add_sample(library)
    assert (book.isbn, book.title, book.author, book.available) == ("A1", "Мастер и Маргарита", "Булгаков", True)
    assert library.find_book("A1") == book


def test_strip_fields(library):
    book = library.add_book(" A1 ", " Мастер ", " Булгаков ")
    assert (book.isbn, book.title, book.author) == ("A1", "Мастер", "Булгаков")


def test_duplicate_does_not_change_catalog(library):
    add_sample(library)
    before = library.list_books()
    with pytest.raises(ValueError, match="уже существует"):
        library.add_book("A1", "Другая", "Другой")
    assert library.list_books() == before


@pytest.mark.parametrize("value", [None, "", " ", 123, True])
def test_invalid_isbn(library, value):
    with pytest.raises(ValueError, match="ISBN"):
        library.add_book(value, "Название", "Автор")
    assert library.list_books() == ()


@pytest.mark.parametrize("value", [None, "", "   ", 42])
def test_invalid_title(library, value):
    with pytest.raises(ValueError, match="Название"):
        library.add_book("A1", value, "Автор")
    assert library.list_books() == ()


@pytest.mark.parametrize("value", [None, "", "   ", 42])
def test_invalid_author(library, value):
    with pytest.raises(ValueError, match="Автор"):
        library.add_book("A1", "Название", value)
    assert library.list_books() == ()


def test_book_immutable(library):
    book = add_sample(library)
    with pytest.raises(FrozenInstanceError):
        book.title = "Нельзя менять"


def test_list_sorted_by_isbn(library):
    add_sample(library, "B2")
    add_sample(library, "A1")
    assert [b.isbn for b in library.list_books()] == ["A1", "B2"]


def test_find_by_isbn(library):
    book = add_sample(library)
    assert library.find_book(" A1 ") == book


def test_find_by_title_case_insensitive(library):
    add_sample(library)
    assert library.find_book("МАСТЕР").isbn == "A1"


def test_find_missing_returns_none(library):
    add_sample(library)
    assert library.find_book("Неизвестно") is None


def test_search_multiple_title_matches(library):
    add_sample(library, "B2", "Большая книга")
    add_sample(library, "A1", "Малая книга")
    assert [b.isbn for b in library.search_books("КНИГА")] == ["A1", "B2"]


def test_search_exact_isbn(library):
    add_sample(library, "A1")
    assert [b.isbn for b in library.search_books("A1")] == ["A1"]


@pytest.mark.parametrize("query", [None, "", " ", 5])
def test_invalid_search_query(library, query):
    with pytest.raises(ValueError, match="Поисковый запрос"):
        library.find_book(query)
    with pytest.raises(ValueError, match="Поисковый запрос"):
        library.search_books(query)


def test_borrow_success(library):
    add_sample(library)
    book = library.borrow_book(" A1 ", " R1 ")
    assert not book.available and book.borrowed_by == "R1"
    assert library.find_book("A1") == book


def test_borrow_twice_preserves_first_reader(library):
    add_sample(library)
    library.borrow_book("A1", "R1")
    before = library.list_books()
    with pytest.raises(ValueError, match="Книга уже выдана"):
        library.borrow_book("A1", "R2")
    assert library.list_books() == before


def test_borrow_unknown_book(library):
    with pytest.raises(KeyError, match="Книга не найдена"):
        library.borrow_book("X1", "R1")


@pytest.mark.parametrize("reader", [None, "", " ", 15])
def test_invalid_reader_does_not_borrow(library, reader):
    add_sample(library)
    with pytest.raises(ValueError, match="ID читателя"):
        library.borrow_book("A1", reader)
    assert library.find_book("A1").available


def test_return_success(library):
    add_sample(library)
    library.borrow_book("A1", "R1")
    returned = library.return_book("A1")
    assert returned.available and returned.borrowed_by is None


def test_return_not_borrowed_preserves_catalog(library):
    add_sample(library)
    before = library.list_books()
    with pytest.raises(ValueError, match="Книга не была выдана"):
        library.return_book("A1")
    assert library.list_books() == before


def test_return_unknown_book(library):
    with pytest.raises(KeyError, match="Книга не найдена"):
        library.return_book("X1")


def test_borrow_again_after_return(library):
    add_sample(library)
    library.borrow_book("A1", "R1")
    library.return_book("A1")
    book = library.borrow_book("A1", "R2")
    assert book.borrowed_by == "R2"


def test_find_follows_new_status(library):
    add_sample(library)
    before = library.find_book("A1")
    library.borrow_book("A1", "R1")
    after = library.find_book("A1")
    assert before.available and not after.available


@pytest.mark.parametrize("isbn", [None, "", " ", 15])
def test_invalid_borrow_isbn(library, isbn):
    with pytest.raises(ValueError, match="ISBN"):
        library.borrow_book(isbn, "R1")


@pytest.mark.parametrize("isbn", [None, "", " ", 15])
def test_invalid_return_isbn(library, isbn):
    with pytest.raises(ValueError, match="ISBN"):
        library.return_book(isbn)
