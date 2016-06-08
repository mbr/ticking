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

# delay: sleep a number of seconds
delay = time.sleep


class Clock(object):
    def __init__(self, tick_len=1.0, start=None):
        """Construct a new clock.

        :param tick_len: Tick length, in seconds.
        :param started_at: A value returned by ``time_src``. Can be passed to
                           sync up multiple Clocks.
        """
        self.tick_len = tick_len
        self.started_at = time_src() if start is None else start

    def wait_until_next_tick(self, now=None):
        """Waits until the start of the next tick, then returns that ticks
        number.

        Ticks are always relative to the construction of the Clock object.

        :return: The tick number of the beginning tick."""
        now = now if now is not None else time_src()

        if now < self.started_at:
            # this should only happen on wraparounds or when using time.time
            # (Python 2)
            raise ValueError(
                'Time-traveling detected. Current time is before start time.')

        # which tick are we inside?
        current_tick = int((now - self.started_at) // self.tick_len)

        next_tick_at = self.started_at + (current_tick + 1) * self.tick_len

        delay(next_tick_at - now)
        return current_tick + 1

    def __iter__(self):
        """Iterate over ticks.

        :return: An iterator yielding ``(tick_num, t)``, where ``t`` is the
                 relative time of the frame.
        """
        while True:
            n = self.wait_until_next_tick()
            yield n, self.tick_len * n


class Stopwatch(object):
    TPL_NOT_STARTED = '{self.title}: not started'
    TPL_FINISHED = '{self.title}: took {self.total:2.2f}s'
    TPL_IN_PROGRESS = '{self.title}: running since {self.total:2.2f}s'

    def __init__(self, title=None):
        """A Stopwatch for measing time.

        Call ``begin()`` and ``finish()`` to start/stop. The ``total``
        property contains the total time elapsed. Can be used as a context
        manager.

        :param title: An optional title for pretty printing.
        """
        self.title = title
        self.start = None
        self.end = None

    def begin(self):
        """Begin time measurement."""
        self.start = time_src()
        return self

    def finish(self):
        """End measuring."""
        self.end = time_src()

    __enter__ = begin

    def __exit__(self, type, value, traceback):
        self.finish()

    @contextmanager
    def __call__(self, *args, **kwargs):
        self.start = time_src()
        yield self
        self.end = time_src()

    @property
    def total(self):
        """Returns the total number of seconds elapsed."""
        if self.start is None:
            return 0

        end = self.end if self.end is not None else time_src()
        return end - self.start

    def __str__(self):
        if self.start is None:
            return self.TPL_NOT_STARTED.format(self)
        if self.end is not None:
            return self.TPL_FINISHED.format(self=self)
        return self.TPL_IN_PROGRESS.format(self=self)


# profiling features
@contextmanager
def profiled(output_filename=None):
    """Load profiling extension and create a profile, saving if requested.

    This contextmanager will load the `cProfile` extension, falling back on
    `profile` if it cannot be imported. A profile will be started before the
    contained block is executed. Afterwards, the profile will be stopped.

    The profile object is yielded back, but should be used only after the
    contextmanager.

    If an optional `output_filename` is supplied, upon exiting the context
    the profile will be saved to the supplied filename.

    :param output_filename: File to store profiling information in.
    """

    # load profiling only if requested
    try:
        import cProfile as profile
    except ImportError:
        import profile

    p = profile.Profile()

    # enabled profiling and run
    p.enable()
    try:
        yield p
    finally:
        p.disable()

        if output_filename is not None:
            p.dump_stats(output_filename)
