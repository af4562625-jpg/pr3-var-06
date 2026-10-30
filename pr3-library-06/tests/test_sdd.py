"""SDD: независимые примеры из CSV, без вычисления эталона программой."""
import csv
import json
from pathlib import Path
import pytest
from implementation import LibraryManager

CSV = Path(__file__).resolve().parents[1] / "specifications" / "examples.csv"
with CSV.open(encoding="utf-8-sig", newline="") as file:
    EXAMPLES = list(csv.DictReader(file))


def catalog_state(library):
    return [
        {"isbn": b.isbn, "title": b.title, "author": b.author, "borrowed_by": b.borrowed_by}
        for b in library.list_books()
    ]


def execute(library, action):
    op = action["op"]
    if op == "add":
        return library.add_book(action["isbn"], action["title"], action["author"])
    if op == "borrow":
        return library.borrow_book(action["isbn"], action["reader"])
    if op == "return":
        return library.return_book(action["isbn"])
    if op == "search":
        return [b.isbn for b in library.search_books(action["query"])]
    raise AssertionError(f"Неизвестная операция в спецификации: {op}")


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda row: row["case_id"])
def test_specification(example):
    library = LibraryManager()
    for book in json.loads(example["books"]):
        library.add_book(book["isbn"], book["title"], book["author"])

    actual_search = None
    captured_error = None
    for action in json.loads(example["actions"]):
        try:
            result = execute(library, action)
            if action["op"] == "search":
                actual_search = result
        except (ValueError, KeyError) as exc:
            captured_error = exc.args[0]
            break

    expected_error = example["expected_error"] or None
    assert captured_error == expected_error
    assert catalog_state(library) == json.loads(example["expected_catalog"])
    if example["expected_search"]:
        assert actual_search == json.loads(example["expected_search"])
