"""Используем один API для этапов TDD: RED, GREEN, FINAL.

По умолчанию импортируется обычный модуль финальной версии,
что позволяет измерять покрытие при тестировании.
"""
import os

_STAGE = os.environ.get("LIBRARY_IMPL", "final").lower()
if _STAGE not in {"red", "green", "final"}:
    raise ValueError("LIBRARY_IMPL принимает red, green или final")

if _STAGE == "final":
    from library_manager import LibraryManager
else:
    import importlib.util
    from pathlib import Path

    source = Path(__file__).resolve().parent / "stages" / _STAGE / "library_manager.py"
    spec = importlib.util.spec_from_file_location(f"library_{_STAGE}", source)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не найден код этапа: {_STAGE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    LibraryManager = module.LibraryManager
