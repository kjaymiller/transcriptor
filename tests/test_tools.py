import pytest
import transcriptor.tools as tools
from datetime import timedelta

@pytest.mark.parametrize('second_val, result', [
        (61.1, "01.100"), # tests leading zeroes
        (130.1000001, "10.100"), # tests that milliseconds returned, not micro
        (36001.123567, "01.123"), # It does not round
        ])
def test_adjust_microseconds_returns_seconds_and_minutes(second_val: float,
        result: str):
    """Tests when passed a timedelta it returns the remaining seconds and
    milliseconds as a string"""

    seconds=timedelta(seconds=second_val)
    assert tools.adjust_microseconds(seconds) == result

@pytest.mark.parametrize('time_val', ["01:23:34,123", "01:23:34.123"])
def test_timedelta_from_str_accepts_comma_or_period(time_val):
    assert tools.timedelta_from_str(time_val) == timedelta(seconds=5014, microseconds=123000)


def test_timedelta_to_dict():
    a = tools.timedelta_to_dict(timedelta(seconds=3661.123))
    assert a['hours'] == 1
    assert a['minutes'] == 1
    assert str(a['seconds'])[:5] == '1.123' #floats are hard
