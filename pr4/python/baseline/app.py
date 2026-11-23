"""Консольное приложение по варианту 06. Данные хранятся до закрытия."""
import argparse
from library_manager import LibraryManager
from models import Book


def show_book(book: Book) -> str:
    status = "доступна" if book.available else f"выдана читателю {book.borrowed_by}"
    return f"[{book.isbn}] {book.title} — {book.author} ({status})"


def demo() -> None:
    library = LibraryManager()
    library.add_book("9785170906309", "Мастер и Маргарита", "М. Булгаков")
    library.add_book("9785170906308", "Преступление и наказание", "Ф. Достоевский")
    library.add_book("9785170906307", "Евгений Онегин", "А. Пушкин")
    print("=== Демонстрация: система управления библиотекой ===")
    print("Добавлено книг:", len(library.list_books()))
    print("Поиск по названию 'МАСТЕР':", show_book(library.find_book("МАСТЕР")))
    print("Выдача:", show_book(library.borrow_book("9785170906309", "reader01")))
    try:
        library.borrow_book("9785170906309", "reader02")
    except (ValueError, KeyError) as error:
        print("Ожидаемый отказ:", error.args[0])
    print("Возврат:", show_book(library.return_book("9785170906309")))
    print("Итоговый каталог:")
    for book in library.list_books():
        print(" ", show_book(book))


def interactive() -> None:
    library = LibraryManager()
    actions = {
        "1": "Добавить книгу", "2": "Найти книгу", "3": "Выдать книгу",
        "4": "Вернуть книгу", "5": "Посмотреть каталог", "0": "Выход",
    }
    while True:
        print("\n=== БИБЛИОТЕКА — ВАРИАНТ 06 ===")
        for k, name in actions.items():
            print(f"{k}. {name}")
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("До свидания!")
            return
        try:
            if choice == "1":
                book = library.add_book(input("ISBN: "), input("Название: "), input("Автор: "))
                print("Добавлено:", show_book(book))
            elif choice == "2":
                found = library.search_books(input("ISBN или фрагмент названия: "))
                if not found:
                    print("Книги не найдены")
                for book in found:
                    print(show_book(book))
            elif choice == "3":
                book = library.borrow_book(input("ISBN: "), input("ID читателя: "))
                print("Выдано:", show_book(book))
            elif choice == "4":
                book = library.return_book(input("ISBN: "))
                print("Возвращено:", show_book(book))
            elif choice == "5":
                items = library.list_books()
                if not items:
                    print("Каталог пуст")
                for book in items:
                    print(show_book(book))
            else:
                print("Нет такого пункта меню")
        except (KeyError, ValueError) as error:
            print("Ошибка:", error.args[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Управление библиотекой (вариант 06)")
    parser.add_argument("--demo", action="store_true", help="Показать демонстрацию и завершить")
    options = parser.parse_args()
    demo() if options.demo else interactive()
