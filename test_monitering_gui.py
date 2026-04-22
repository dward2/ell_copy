import pytest
from monitering_gui import get_apnea_color, get_latest_time, format_time

def test_returns_red():
    assert get_apnea_color(3) == 'red'


def test_returns_black():
    assert get_apnea_color(2) == 'black'


def test_empty():
    assert get_apnea_color('-') == 'black'

from datetime import datetime

def test_get_latest_time_basic():
    times = [
        datetime(2024, 1, 1, 10, 0),
        datetime(2024, 1, 1, 12, 0),
        datetime(2024, 1, 1, 9, 0),
    ]
    assert get_latest_time(times) == datetime(2024, 1, 1, 12, 0)


def test_get_latest_time_empty():
    assert get_latest_time([]) is None


def test_get_latest_time_single():
    t = datetime(2024, 1, 1, 10, 0)
    assert get_latest_time([t]) == t


def test_format_time_standard():
    dt = datetime(2025, 1, 5, 14, 30, 45)
    assert format_time(dt) == "01/05/25 14:30:45"


def test_format_time_zero_padding():
    dt = datetime(2026, 1, 5, 4, 3, 2)
    assert format_time(dt) == "01/05/26 04:03:02"