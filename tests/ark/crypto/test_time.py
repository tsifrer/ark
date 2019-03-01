from chain.crypto import time


def test_get_real_time():
    dt = time.get_real_time(45021209)
    assert isinstance(dt, int)
    assert dt == 1535122409
