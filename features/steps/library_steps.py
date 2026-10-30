"""BDD-steps: связь естественно-языковых сценариев и публичного API."""
from behave import given, when, then
from implementation import LibraryManager


@given('в каталоге есть доступная книга с ISBN "{isbn}"')
def step_book_exists(context, isbn):
    context.library.add_book(isbn, "Учебная книга", "Автор")


@given('книгу "{isbn}" уже взял читатель "{reader}"')
def step_book_is_borrowed(context, isbn, reader):
    context.library.borrow_book(isbn, reader)


@given('каталог пуст')
def step_empty_catalog(context):
    assert context.library.list_books() == ()


@when('читатель "{reader}" берет книгу "{isbn}"')
def step_borrow(context, reader, isbn):
    context.error = None
    try:
        context.result = context.library.borrow_book(isbn, reader)
    except (KeyError, ValueError) as exc:
        context.error = exc


@when('библиотекарь принимает возврат книги "{isbn}"')
def step_return(context, isbn):
    context.error = None
    try:
        context.result = context.library.return_book(isbn)
    except (KeyError, ValueError) as exc:
        context.error = exc


@when('библиотекарь ищет книги по запросу "{query}"')
def step_search(context, query):
    context.result = context.library.search_books(query)


@when('библиотекарь повторно добавляет книгу с ISBN "{isbn}"')
def step_add_duplicate(context, isbn):
    context.error = None
    try:
        context.library.add_book(isbn, "Подменённое название", "Другой автор")
    except (KeyError, ValueError) as exc:
        context.error = exc


@then('книга "{isbn}" выдана читателю "{reader}"')
def step_borrowed(context, isbn, reader):
    book = context.library.find_book(isbn)
    assert book is not None
    assert not book.available
    assert book.borrowed_by == reader


@then('книга "{isbn}" доступна для выдачи')
def step_available(context, isbn):
    book = context.library.find_book(isbn)
    assert book is not None
    assert book.available
    assert book.borrowed_by is None


@then('появляется ошибка "{message}"')
def step_error(context, message):
    assert context.error is not None, f"Ожидали ошибку {message!r}, но её не было"
    assert context.error.args[0] == message


@then('поиск возвращает ISBN "{isbn}"')
def step_search_result(context, isbn):
    assert tuple(book.isbn for book in context.result) == (isbn,)


@then('в каталоге только одна книга с ISBN "{isbn}"')
def step_only_one_book(context, isbn):
    assert tuple(book.isbn for book in context.library.list_books()) == (isbn,)
    assert context.library.find_book(isbn).title == "Учебная книга"


@then('каталог по-прежнему пуст')
def step_still_empty(context):
    assert context.library.list_books() == ()
