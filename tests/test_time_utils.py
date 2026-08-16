from sherlocked.utils.time_utils import chrome_time


def test_chrome_time_conversion():
    result = chrome_time(13253760000000000)

    assert result.year == 2020
    assert result.month == 12
    assert result.day == 30


def test_chrome_zero_time():
    result = chrome_time(0)

    assert result is None

def test_chrome_invalid_timestamp():
    result = chrome_time("not-a-timestamp")

    assert result is None