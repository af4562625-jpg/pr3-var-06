# Практическая работа № 3 — вариант 06 «Система управления библиотекой»

Дисциплина: **Тестирование и верификация ПО**. Задание: разработать один программный продукт и продемонстрировать подходы **TDD, ATDD, BDD, SDD**.

## Функциональность

- Добавление книги (ISBN, название, автор).
- Поиск по точному ISBN или фрагменту названия (без учёта регистра).
- Выдача доступной книги конкретному читателю.
- Возврат выданной книги.
- Просмотр отсортированного каталога и обработка ошибочных действий.

Учебные ограничения: **один экземпляр на ISBN**, ISBN рассматривается как непустой уникальный идентификатор без проверки контрольной суммы; нет удаления, авторизации и постоянного хранилища. Данные существуют только до закрытия программы.

## Запуск программы

Нужен **Python 3.10 или новее**. Выполняйте команды из корневой папки проекта.

```bash
python app.py
```

Быстрая демонстрация без ввода:

```bash
python app.py --demo
```

Меню предлагает добавить, найти, выдать и вернуть книгу. Попытка повторной выдачи или возврата доступной книги вызывает понятное сообщение и не меняет состояние.

## Установка библиотек для тестирования

```bash
python -m pip install -r requirements.txt
```

### TDD: RED → GREEN → REFACTOR

Три **сохранённые версии** одной реализации; тесты одинаковые на всех этапах.

- `stages/red/library_manager.py`: заглушки с `NotImplementedError`.
- `stages/green/library_manager.py`: минимальная работающая реализация.
- `library_manager.py`: итоговая версия после рефакторинга.

**Windows PowerShell:**

```powershell
$env:LIBRARY_IMPL = "red"; python -m pytest -q tests/test_tdd.py
$env:LIBRARY_IMPL = "green"; python -m pytest -q tests/test_tdd.py
$env:LIBRARY_IMPL = "final"; python -m pytest -q tests/test_tdd.py
Remove-Item Env:LIBRARY_IMPL
```

**Linux/macOS:**

```bash
LIBRARY_IMPL=red python -m pytest -q tests/test_tdd.py
LIBRARY_IMPL=green python -m pytest -q tests/test_tdd.py
LIBRARY_IMPL=final python -m pytest -q tests/test_tdd.py
```

Красные тесты на этапе RED — **ожидаемая часть методики**, не результат сломанной финальной программы.

### ATDD — критерии приёмки

Пять тестов проверяют добавление и поиск, выдачу и возврат, защиту от дубликатов, повторной выдачи и неизвестных книг.

```bash
python -m pytest -q tests/test_atdd.py
```

### BDD — Given / When / Then

Семь сценариев написаны в `features/planning.feature`, определения шагов — в `features/steps/library_steps.py`.

```bash
python -m behave --no-capture
```

### SDD — Specification by Example

Десять строк в `specifications/examples.csv` содержат входные данные, операции и **заранее заданный** ожидаемый результат. Тест параметризуется по строкам таблицы.

```bash
python -m pytest -q tests/test_sdd.py
```

### Все тесты, отчёты и покрытие

```bash
python -m pytest -q tests
python -m coverage run --branch --source=library_manager -m pytest -q tests
python -m coverage report -m
python scripts/check_console.py
python scripts/run_checks.py
```

Последняя команда сохраняет результаты отдельных запусков в `results/`. Она **ожидает неуспешный** код возврата RED, а отсутствие пакета `behave` явно помечает как «не запускалось».

После публикации GitHub Actions запускается автоматически при `push` и проверяет все три группы pytest, BDD, покрытие и демонстрацию приложения на Python 3.12. Статус выполнения — вкладка **Actions** репозитория.

## Структура проекта

```text
pr3-library-06/
├── app.py                           # Консольное меню + демонстрация
├── library_manager.py               # Финальная бизнес-логика
├── models.py                        # Неизменяемая модель Book
├── implementation.py                # Выбор RED / GREEN / FINAL
├── requirements.txt                 # Библиотеки для тестирования
├── tests/
│   ├── conftest.py
│   ├── test_tdd.py
│   ├── test_atdd.py
│   └── test_sdd.py
├── stages/
│   ├── red/library_manager.py
│   └── green/library_manager.py
├── features/
│   ├── planning.feature
│   ├── environment.py
│   └── steps/library_steps.py
├── specifications/examples.csv
├── scripts/
│   ├── check_console.py
│   └── run_checks.py
├── results/                         # Протоколы реальных запусков
└── .github/workflows/tests.yml      # Автоматическая проверка на GitHub
```

## Что продемонстрировать на защите

1. `python app.py --demo` — добавление, поиск, выдача, отклонение второй выдачи и возврат.
2. RED: ошибки `NotImplementedError` в тестах до реализации.
3. GREEN и FINAL: успешные тесты на том же наборе.
4. ATDD: соблюдение согласованных критериев.
5. BDD: человекочитаемые сценарии и успешный запуск Behave.
6. SDD: таблица конкретных примеров и её проверка.
7. `coverage report -m` — измеренное покрытие финального основного модуля.

_Протоколы — результаты запуска; показания локального окружения могут отличаться по версии Python/пакетов и времени выполнения. Полное покрытие не гарантирует отсутствие всех ошибок._
