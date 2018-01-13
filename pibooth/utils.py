# -*- coding: utf-8 -*-

import time
import contextlib


@contextlib.contextmanager
def timeit(description):
    print(description)
    start = time.time()
    try:
        yield
    finally:
        print("    -> took {} seconds.".format(time.time() - start))
