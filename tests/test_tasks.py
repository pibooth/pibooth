# -*- coding: utf-8 -*-

import time
from pibooth.tasks import AsyncTask

RESULT = {"Hello": "World"}


def exec_foo(duration):
    time.sleep(duration)
    return RESULT


def test_simple_task(init_tasks):
    task = AsyncTask(exec_foo, (2,))
    assert task.is_alive() is True
    assert task.wait() == RESULT
    assert task.is_alive() is False
    assert task.result() == RESULT


def test_unfinished_task(init_tasks):
    task = AsyncTask(exec_foo, (2,))
    assert task.result() is None
    assert task.is_alive() is True


def test_kill_tasks(init_tasks):
    task = AsyncTask(exec_foo, (0.5,), loop=True)
    time.sleep(1)
    assert task.is_alive() is True
    task.kill()
    assert task.is_alive() is False
    assert task.result() == RESULT
