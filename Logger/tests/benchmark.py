import timeit
import cProfile
import memory_profiler
import sys

sys.path.append(r'D:\GitHub\Repos\Logger\Logger')


from logging_lib.logger_main import Logger

logger = Logger()

class timeit_tests:

    def __init__(self, n):

        logger.log("Running timeit tests\n", "INTERNAL")
        self.n = n


    def bench_test_plaintext(self):
        logger.log("Test", "DEBUG")

    def bench_test_plaintext_plainexception(self):
        logger.log("Test", "DEBUG", exception_traceback=ValueError)

    def bench_test_plaintext_withfile(self):
        logger.log("Test", "DEBUG", is_file=True)

    def bench_test_plaintext_plainexception_withfile(self):
        logger.log("Test", "DEBUG", exception_traceback=ValueError, is_file=True)

    def bench_timeit_plaintext(self):
        exe_time = timeit.timeit(lambda: self.bench_test_plaintext(), number=self.n)
        avg = (exe_time / self.n)
        return (f"[timeit] [plaintext] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {self.n}")

    def bench_timeit_plaintext_plainexception(self):
        exe_time = timeit.timeit(lambda: self.bench_test_plaintext_plainexception(), number=self.n)
        avg = (exe_time / self.n)
        return (f"[timeit] [plaintext] [plainexception] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {self.n}")

    def bench_timeit_plaintext_withfile(self):
        exe_time = timeit.timeit(lambda: self.bench_test_plaintext_withfile(), number=self.n)
        avg = (exe_time / self.n)
        return (f"[timeit] [plaintext] [withfile] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {self.n}")

    def bench_timeit_plaintext_plainexception_withfile(self):
        exe_time = timeit.timeit(lambda: self.bench_test_plaintext_plainexception_withfile(), number=self.n)
        avg = (exe_time / self.n)
        return (f"[timeit] [plaintext] [plainexception] [withfile] Total time: {exe_time:.4f} Average time: {avg:.8f} Repeats: {self.n}")

    def bench(self):

        message = []

        tests = (self.bench_timeit_plaintext,
        self.bench_timeit_plaintext_plainexception)

        for function in tests:
            message.append(function())

        logger.log("\n" + '\n'.join(message), "INFO")


class cProfile_tests:

    def __init__(self, n):

        self.n = n
        logger.log("Running cProfile tests\n", "INTERNAL")

    def cprofile_plaintext_test(self):
        for i in range(self.n):
            logger.log("Test", "INFO")

    def cprofile_plaintext(self):
        cProfile.runctx('self.cprofile_plaintext_test()', globals=globals(), locals=locals())

timeit_tests = timeit_tests(10000)

timeit_tests.bench()








    


