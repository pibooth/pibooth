# -*- coding: utf-8 -*-

"""Pibooth asynchron tasks.
"""

import threading
from concurrent import futures

from pibooth import evts

class AsyncTasksPool(object):

    FUTURES = {}

    def __init__(self):
        if not AsyncTask.POOL:
            self._pool = futures.ThreadPoolExecutor()
            AsyncTask.POOL = self
        else:
            self._pool = AsyncTask.POOL._pool

    def start_task(self, task, args):
        "Start an asynchronous task and add future on tracking list."
        assert isinstance(task, AsyncTask)
        future = self._pool.submit(task.run, *args)
        self.FUTURES[future] = task
        future.add_done_callback(self.finish_task)
        return future
    
    def finish_task(self, future):
        """Remove future from tracking list.
        """
        self.FUTURES.pop(future)
        future.result()  # Raise exception if occures during run

    def quit(self):
        """Stop all tasks and don't accept new one.
        """
        for task in self.FUTURES.values():
            task.kill()
        self.FUTURES.clear()
        self._pool.shutdown(wait=True)


class AsyncTask(object):

    POOL = None

    def __init__(self, runnable, args=(), event=None, loop=False):
        self._stop_event = threading.Event()
        self.runnable = runnable
        self.event_type = event
        self.loop = loop
        self.future = self.POOL.start_task(self, args)

    def run(self, *args, **kwargs):
        """Execute the runnable.
        """
        result = None
        while not self._stop_event.is_set():
            result = self.runnable(*args, **kwargs)
            self.emit(result)
            if not self.loop:
                break
        return result

    def emit(self, data):
        """Post event with the result of the task.
        """
        if self.event_type is not None:
            evts.post(self.event_type, result=data)

    def result(self):
        """Return task result.
        """
        return self.future.result()

    def is_alive(self):
        """Return true if the task is not yet started or running.
        """
        return not self.future.done()

    def wait(self, timeout=None):
        """Wait for task ends or cancelled.
        """
        try:
            return self.future.result(timeout)
        except futures.TimeoutError:
            raise
        except Exception:
            return None

    def kill(self):
        """Stop running.
        """
        self._stop_event.set()
        self.future.cancel()
        self.wait(30)  # Max 30 seconds
