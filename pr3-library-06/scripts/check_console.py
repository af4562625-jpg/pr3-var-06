"""Три проверки реального консольного интерфейса через subprocess."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_app(*args, input_text=""):
    result = subprocess.run(
        [sys.executable, "app.py", *args], input=input_text, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding="utf-8", cwd=ROOT, timeout=15, check=True,
    )
    return result.stdout


def main():
    demo = run_app("--demo")
    assert "Добавлено книг: 3" in demo
    assert "Книга уже выдана" in demo
    assert "Возврат:" in demo
    print("PASS C01 — демонстрация (--demo)")

    transcript = run_app(input_text=(
        "1\nA1\nУчебная книга\nАвтор\n"
        "2\nA1\n3\nA1\nR1\n3\nA1\nR2\n4\nA1\n5\n0\n"
    ))
    assert "Добавлено:" in transcript
    assert "Выдано:" in transcript
    assert "Ошибка: Книга уже выдана" in transcript
    assert "Возвращено:" in transcript
    assert "До свидания!" in transcript
    print("PASS C02 — добавление, поиск, выдача, отказ и возврат")

    invalid = run_app(input_text="5\n999\n1\nA1\nНазвание\nАвтор\n3\nX1\nR1\n0\n")
    assert "Каталог пуст" in invalid
    assert "Нет такого пункта меню" in invalid
    assert "Ошибка: Книга не найдена" in invalid
    print("PASS C03 — пустой каталог и ошибки ввода")


if __name__ == "__main__":
    main()
