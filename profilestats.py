from cProfile import Profile
from functools import wraps
import pstats
import threading
import pyprof2calltree

profiler = Profile()
lock = threading.Lock()

def profile(cumulative=True, print_stats=0, sort_stats='cumulative',
            dump_stats=False, profile_filename='profilestats.out',
            callgrind_filename='callgrind.out', should_profile=None):
    def closure(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if should_profile and not should_profile():
                return func(*args, **kwargs)
            result = None
            if cumulative:
                global profiler
            else:
                profiler = Profile()
            try:
                result = profiler.runcall(func, *args, **kwargs)
            finally:
                if lock.acquire(False):
                    if dump_stats:
                        profiler.dump_stats(profile_filename)
                    if callgrind_filename:
                        stats = pstats.Stats(profiler)
                        conv = pyprof2calltree.CalltreeConverter(stats)
                        with open(callgrind_filename, 'w') as fd:
                            conv.output(fd)
                        if print_stats:
                            stats.strip_dirs().sort_stats(
                                sort_stats).print_stats(print_stats)
                    lock.release()
                    return result
            return result
        return decorator
    return closure
