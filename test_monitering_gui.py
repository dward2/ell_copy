import pytest
from monitering_gui import get_apnea_color


def test_returns_red():
    assert get_apnea_color('3') == 'red'


def test_returns_black():
    assert get_apnea_color(2) == 'black'


def test_empty():
    assert get_apnea_color('-') == 'black'
