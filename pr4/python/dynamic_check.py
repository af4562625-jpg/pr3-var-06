"""Real CPU/memory profiling and independent functional checks of one version."""
import argparse
import cProfile
import importlib
import io
from pathlib import Path
import pstats
import sys
import tracemalloc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--profile', type=Path)
    parser.add_argument('--expect-failures', type=int, default=0)
    args = parser.parse_args()
    source = args.source.resolve()
    if not (source / 'library_manager.py').is_file():
        parser.error(f'No library_manager.py in {source}')
    sys.path.insert(0, str(source))
    manager = importlib.import_module('library_manager').LibraryManager

    def workload():
        library = manager()
        for index in range(2000):
            library.add_book(str(index), f'Book {index}', 'Author')
        # Title queries exercise substring search instead of the ISBN shortcut.
        for index in range(100):
            library.search_books(f'Book {index}')
        return library

    print(f'SOURCE: python/{source.name}/library_manager.py')
    print('WORKLOAD: 2000 books; 100 title searches')
    tracemalloc.start()
    profiler = cProfile.Profile()
    try:
        profiler.enable()
        library = workload()
        profiler.disable()
        current, peak = tracemalloc.get_traced_memory()
        snapshot = tracemalloc.take_snapshot()
    finally:
        profiler.disable()
        tracemalloc.stop()
    print(f'tracemalloc current bytes: {current}')
    print(f'tracemalloc peak bytes: {peak}')
    print(f'Retained books: {len(library.list_books())}')
    print('tracemalloc top 3 allocation lines:')
    for stat in snapshot.statistics('lineno')[:3]:
        frame = stat.traceback[0]
        print(f'  {Path(frame.filename).name}:{frame.lineno}: {stat.size} bytes; {stat.count} blocks')
    if args.profile:
        args.profile.parent.mkdir(parents=True, exist_ok=True)
        profiler.dump_stats(str(args.profile))
    output = io.StringIO()
    pstats.Stats(profiler, stream=output).strip_dirs().sort_stats('cumulative').print_stats(8)
    print('cProfile (top 8 by cumulative time):')
    print(output.getvalue())

    def double_loan():
        library = manager()
        library.add_book('1', 'Alpha', 'Author')
        library.borrow_book('1', 'R1')
        try:
            library.borrow_book('1', 'R2')
        except ValueError:
            return True
        return False

    def returned_book():
        library = manager()
        library.add_book('1', 'Alpha', 'Author')
        library.borrow_book('1', 'R1')
        library.return_book('1')
        return library.find_book('1').available

    def partial_search():
        library = manager()
        library.add_book('1', 'Alpha', 'Author')
        return len(library.search_books('lph')) == 1

    failures = 0
    for name, check in (('DOUBLE_LOAN', double_loan), ('RETURN', returned_book),
                        ('PARTIAL_SEARCH', partial_search)):
        try:
            passed = check()
            detail = ''
        except Exception as error:
            passed = False
            detail = f' ({type(error).__name__}: {error})'
        failures += not passed
        print(f"{name}: {'PASS' if passed else 'FAIL'}{detail}")
    print(f'BEHAVIOR: {3 - failures}/3 passed; expected failures={args.expect_failures}')
    return 0 if failures == args.expect_failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
