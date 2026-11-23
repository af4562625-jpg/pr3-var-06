import cProfile, io, pstats, sys, tracemalloc
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from library_manager import LibraryManager

def workload():
    lib=LibraryManager()
    for i in range(2000): lib.add_book(str(i),'Book '+str(i),'Author')
    for i in range(100): lib.search_books(str(i))
    return lib
tracemalloc.start(); profiler=cProfile.Profile(); profiler.enable(); lib=workload(); profiler.disable()
current, peak=tracemalloc.get_traced_memory()
print('tracemalloc current/peak bytes:',current,peak)
out=io.StringIO(); pstats.Stats(profiler,stream=out).sort_stats('cumulative').print_stats(12);print(out.getvalue())
a=LibraryManager();a.add_book('1','Alpha','Author');a.borrow_book('1','R1')
try: a.borrow_book('1','R2'); print('DOUBLE_LOAN: FAIL (accepted)')
except ValueError: print('DOUBLE_LOAN: PASS')
a.return_book('1'); print('RETURN:', 'PASS' if a.find_book('1').available else 'FAIL')
print('PARTIAL_SEARCH:', 'PASS' if a.search_books('lph') else 'FAIL')
