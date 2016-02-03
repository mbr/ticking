from contextlib import contextmanager
import time

# FIXME: use PEP0418 routines for better accuracy and monotonic time#
#        source


class Clock(object):
    def __init__(self, tick_len=1.0, start=None):
        self.tick_len = tick_len
        self.restart(start)

    def restart(self, start=None):
        self.started_at = start or time.time()

    def wait_until_next_tick(self, now):
        now = now or time.time()

        if now < self.started_at:
            raise ValueError(
                'Time-traveling detected. Current time is before start time.')

        current_tick = int((now - self.started_at) // self.tick_len)
        next_tick_at = self.started_at + (current_tick + 1) * self.tick_len

        assert next_tick_at >= now

        time.sleep(next_tick_at - now)
        return current_tick + 1

    def __call__(self):
        while True:
            now = time.time()

            yield self.wait_until_next_tick(now), now


class Stopwatch(object):
    TPL = '{0.title}: took {0.total:2.2f}s'

    def __init__(self, title=None):
        self.title = title

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        self.end = time.time()

    @contextmanager
    def __call__(self, *args, **kwargs):
        self.start = time.time()
        yield self
        self.end = time.time()

    @property
    def total(self):
        return self.end - self.start

    def __str__(self):
        return self.TPL.format(self)
