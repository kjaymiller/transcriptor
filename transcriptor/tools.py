import re
import typing
from datetime import timedelta


def adjust_microseconds(time_val: timedelta, separator=".") -> str:
    """Take the seconds and microseconds from a timedelta and return 
the the remaining seconds and milliseconds, Not Rounded as a str.
Seconds will have a leading zero."""

    _, seconds = divmod(time_val.seconds, 60)
    return str(seconds).zfill(2) + separator + str(time_val.microseconds)[:3]


def timedelta_from_str(time_str: str) -> timedelta:
    """Given a string in %H:%M:%S,%f, return a timedelta
    >>> timedelta_from_str("01:23:34,123")
    datetime.timedelta(seconds=5014, microseconds=123000)
    """
    time_splitter = r":"
    time_vals = re.split(time_splitter, time_str)
    time_vals[-1] = time_vals[-1].replace(",", ".")  # srt time = H:M:S,Mil

    return timedelta(
        hours=int(time_vals[0]), minutes=int(time_vals[1]), seconds=float(time_vals[2]),
    )


def timedelta_to_dict(time_float: float) -> typing.Dict:
    """Convert the time float from output.json and create a dict"""
    minutes, seconds = divmod(
        time_float.total_seconds(), 60
    )  # seconds will still have microseconds attached
    hours, minutes = divmod(minutes, 60)

    return {"hours": int(hours), "minutes": int(minutes), "seconds": seconds}

    """Convert the time float from output.json and create a timedelta"""
    return timedelta(seconds=time_float)
