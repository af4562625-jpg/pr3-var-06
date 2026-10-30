"""Сохраняет фактические протоколы RED / GREEN / FINAL и покрытия.

Запуск из корня проекта: python scripts/run_checks.py
Behave запускается только когда пакет установлен.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def run(name: str, args: list[str], *, stage="final", expected=0):
    env = os.environ.copy()
    env["LIBRARY_IMPL"] = stage
    process = subprocess.run(
        [sys.executable, *args], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding="utf-8", errors="replace", check=False,
    )
    output = process.stdout
    (RESULTS / f"{name}.txt").write_text(output, encoding="utf-8")
    print(f"{name:>16} : exit={process.returncode} (ожидается {expected})")
    if expected == "nonzero":
        assert process.returncode != 0, f"{name}: этап RED должен провалиться"
    else:
        assert process.returncode == expected, f"{name}: тесты не пройдены\n{output[-2000:]}"


for phase in ("red", "green", "final"):
    run(phase + "_pytest", ["-m", "pytest", "-q", "tests", "--tb=no"],
        stage=phase, expected="nonzero" if phase == "red" else 0)

if importlib.util.find_spec("behave"):
    for phase in ("red", "green", "final"):
        run(phase + "_bdd", ["-m", "behave", "--no-capture", "--format", "progress"],
            stage=phase, expected="nonzero" if phase == "red" else 0)
else:
    (RESULTS / "bdd_status.txt").write_text(
        "BDD NOT RUN: пакет behave отсутствует в этой среде.\n"
        "Установите зависимости: python -m pip install -r requirements.txt\n"
        "Затем: python -m behave --no-capture\n", encoding="utf-8")
    print("             BDD : не выполнено (не установлен behave)")

run("coverage_tests", ["-m", "coverage", "run", "--branch", "--source=library_manager", "-m", "pytest", "-q", "tests"])
run("coverage_report", ["-m", "coverage", "report", "-m"])
run("console_checks", ["scripts/check_console.py"])
run("demo", ["app.py", "--demo"])
print("Протоколы сохранены в:", RESULTS)
