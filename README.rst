ticking
=======

Useful tools when dealing with clocks for timing and benchmarking. Will use a
different method for retrieving accurate, monotonic clock values (see source
for detail).

Tested on Python 2.7 and 3.3+. The latter is recommended because the ``time``
module contains much better access to OS timing functions.

Examples
--------

Simple framerate-limiter:

.. code-block:: pycon

    >>> import ticking
    >>> for frame, t in ticking.Clock(0.5):
    ...   print(frame, t)
    ...
    1 0.5
    2 1.0
    3 1.5
    ...


After dropping a frame, the clock is aligned again:

.. code-block:: pycon

    >>> import time
    >>> for frame, t in ticking.Clock(0.5):
    ...   print(frame, t)
    ...   time.sleep(0.8)  # drop a frame
    ...
    1 0.5
    3 1.5
    5 2.5

Measuring time:

.. code-block:: pycon

    >>> with ticking.Stopwatch('Demonstration') as sw:
    ...   time.sleep(1.3)
    ...
    >>> sw.total
    1.3013252970049507
    >>> print(sw)
    Demonstration: took 1.30s

