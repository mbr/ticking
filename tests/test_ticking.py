import ticking
import time


def test_clock():
    clk = ticking.Clock(tick_len=0.25)

    start = time.time()
    frame_num, t = next(iter(clk))
    end = time.time()

    assert 0.2 < end - start < 0.3
    assert frame_num == 1


def test_dropped_frames():
    clk = ticking.Clock(tick_len=0.25)

    fnum_start = next(iter(clk))[0]
    time.sleep(0.3)
    fnum_end = next(iter(clk))[0]

    assert fnum_end - fnum_start == 2


def test_stopwatch():
    with ticking.Stopwatch() as sw:
        time.sleep(1)

        # check that we can print it mid-run
        '{}'.format(sw)

    assert 0.9 < sw.total < 1.1


def test_profiling():
    with ticking.profiled() as prof:
        time.sleep(0.1)

    import cProfile as profile
    assert isinstance(prof, profile.Profile)
