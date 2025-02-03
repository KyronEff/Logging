import timeit
import cProfile
import pstats
import sys

sys.path.append('D:\GitHub\Repos\Logging\custom_logging_library')


from logging_lib.logger import Logger

logger = Logger()

def bench_test():
    logger.info_log("Test")

n = 1000

def bench_timeit():
    exe_time = timeit.timeit(lambda: bench_test(), number=n)
    avg = (exe_time / n)
    logger.debug_log(f"[timeit] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {n}")

bench_timeit()