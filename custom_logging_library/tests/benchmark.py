import timeit
import cProfile
import pstats
import sys

sys.path.append('D:\GitHub\Repos\Logging\custom_logging_library')


from logging_lib.logger import Logger

logger = Logger()

def bench_test_plaintext():
    logger.info_log("")

def bench_test_plaintext_plainexception():
    logger.info_log("Test", exception=ValueError)

def bench_test_plaintext_withfile():
    logger.info_log("Test", is_file=True)

def bench_test_plaintext_plainexception_withfile():
    logger.info_log("Test", exception=ValueError, is_file=True)


n = 100
final_timeit_logs = []

def bench_timeit_plaintext():
    exe_time = timeit.timeit(lambda: bench_test_plaintext(), number=n)
    avg = (exe_time / n)
    final_timeit_logs.append(f"[timeit] [plaintext] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {n}")

def bench_timeit_plaintext_plainexception():
    exe_time = timeit.timeit(lambda: bench_test_plaintext_plainexception(), number=n)
    avg = (exe_time / n)
    final_timeit_logs.append(f"[timeit] [plaintext] [plainexception] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {n}")

def bench_timeit_plaintext_withfile():
    exe_time = timeit.timeit(lambda: bench_test_plaintext_withfile(), number=n)
    avg = (exe_time / n)
    final_timeit_logs.append(f"[timeit] [plaintext] [withfile] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {n}")

def bench_timeit_plaintext_plainexception_withfile():
    exe_time = timeit.timeit(lambda: bench_test_plaintext_plainexception_withfile(), number=n)
    avg = (exe_time / n)
    final_timeit_logs.append(f"[timeit] [plaintext] [plainexception] [withfile] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {n}")

bench_timeit_plaintext()


logger.debug_log("\n" + '\n'.join(final_timeit_logs))