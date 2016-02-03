from contextlib import contextmanager
import os
import sys
import time

# decide on a clock source to use. while we could craft a context that allows
# configuration on a case-by-case basis, we opt for simplicity here

# time source is our main relative-time function. upon being called, it returns
# a float denoting some time in seconds without a specified starting point.
# it should increase monotonically and be as accurate as possible
time_src = None

if sys.version_info[0] <= 2:
    # Python 2 has rather poor time facilities in the stdlib, which
    # even differ from platform to platform.
    if os.name == 'nt':
        # on windows, time.clock() on Python 2 returns seconds since the
        # the first call to time.clock(). we need to call it once
        time.clock()
        time_src = time.clock
    else:
        # on other systems, we're not so lucky. for example, on linux
        # time.clock() will wrap around fairly quickly (and does not even
        # return seconds. we'll have to fall back to good old time.time() and
        # cross our fingers
        time_src = time.time
else:
    # on Python 3.3 or newer, things are much better
    time_src = time.monotonic

delay = time.sleep


class Clock(object):
    def __init__(self, tick_len=1.0):
        self.tick_len = tick_len
        self.started_at = time_src()

    def wait_until_next_tick(self, now):
        now = now or time_src()

        if now < self.started_at:
            # this should only happen on wraparounds or when using time.time
            # (Python 2)
            raise ValueError(
                'Time-traveling detected. Current time is before start time.')

        current_tick = int((now - self.started_at) // self.tick_len)
        next_tick_at = self.started_at + (current_tick + 1) * self.tick_len

        assert next_tick_at >= now

        delay(next_tick_at - now)
        return current_tick + 1

    def __call__(self):
        while True:
            now = time_src()

            yield self.wait_until_next_tick(now), now


class Stopwatch(object):
    TPL = '{0.title}: took {0.total:2.2f}s'

    def __init__(self, title=None):
        self.title = title

    def __enter__(self):
        self.start = time_src()
        return self

    def __exit__(self, type, value, traceback):
        self.end = time_src()

    @contextmanager
    def __call__(self, *args, **kwargs):
        self.start = time_src()
        yield self
        self.end = time_src()

    @property
    def total(self):
        return self.end - self.start

    def __str__(self):
        return self.TPL.format(self)
