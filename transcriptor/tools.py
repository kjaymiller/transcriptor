import re
import typing
from datetime import timedelta
from .markers import Marker


def str_to_timedelta(time_val: timedelta, separator=".") -> str:
    """Take the seconds and microseconds from a timedelta and return 
the the remaining seconds and milliseconds, Not Rounded as a str.
Seconds will have a leading zero."""

    if time_val.microseconds:
        return str(time_val)[:3]

    else:
        return str(time_val) + ',000'



def timedelta_from_str(time_str: str) -> timedelta:
    """Given a string in %H:%M:%S,%f, return a timedelta
    >>> timedelta_from_str("01:23:34,123")
    datetime.timedelta(seconds=5014, microseconds=123000)
    """
    time_splitter = r":"
    [h, m, s] = re.split(time_splitter, time_str)
    s = s.replace(",", ".")  # srt time = H:M:S,Mil
    return timedelta(hours=int(h), minutes=int(m), seconds=float(s))
