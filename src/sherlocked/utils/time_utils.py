from datetime import datetime, timedelta, timezone


def chrome_time(timestamp):
    """
    Convert a Chrome/WebKit timestamp to a timezone-aware datetime.

    Chrome timestamps are stored as microseconds since
    1601-01-01 00:00:00 UTC.
    """

    if timestamp is None:
        return None

    try:
        timestamp = int(timestamp)
    except (TypeError, ValueError):
        return None

    if timestamp == 0:
        return None

    chrome_epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)

    return chrome_epoch + timedelta(microseconds=timestamp)


def filetime_to_datetime(filetime):

    if filetime == 0:
        return None

    return datetime(1601, 1, 1) + timedelta(
        microseconds=filetime / 10
    )