import pytest
import patient_gui
from patient_gui import validate_name
from patient_gui import validate_mrn
from patient_gui import validate_rn
from patient_gui import validate_pressure
from patient_gui import only_digits


@pytest.mark.parametrize("name , expected", [
    ("Nika Ilieva", True),
    ("Ella Fortenbery", True),
    (" Nika Ilieva ", True),
    ("", "Please enter a patient name."),
    ("  ", "Please enter a patient name."),
    ("John123", "Name invalid"),
    ("John@Carter", "Name invalid"),
])
def test_validate_name(name, expected):
    assert validate_name(name) == expected


@pytest.mark.parametrize("mrn, expected", [
    ("123", True),
    ("123A", "MRN Invalid"),
    ("123!", "MRN Invalid"),
    ("abc", "MRN Invalid"),
    ("", "Please enter Medical Record Number"),
    ("  ", "Please enter Medical Record Number"),

])
def test_validate_mrn(mrn, expected):
    assert validate_mrn(mrn) == expected


@pytest.mark.parametrize("rn, expected", [
    ("101", True),
    ("1", True),
    ("", "Please enter Room Number"),
    ("   ", "Please enter Room Number"),
    ("abc", "Room Number Invalid"),
    ("13a", "Room Number Invalid"),
    ("17.5", "Room Number Invalid"),
    ("!", "Room Number Invalid"),
    ("@", "Room Number Invalid"),
])
def test_validate_rn(rn, expected):
    assert validate_rn(rn) == expected


@pytest.mark.parametrize("pres, expected", [
    ("4", True),
    ("15", True),
    ("25", True),
    ("", True),
    ("   ", True),
    ("abc", "CPAP pressure must be an integer"),
    ("12.5", "CPAP pressure must be an integer"),
    ("3", "CPAP pressure must be between 4 and 25"),
    ("26", "CPAP pressure must be between 4 and 25"),
    ("0", "CPAP pressure must be between 4 and 25"),
    ("-1", "CPAP pressure must be an integer"),
])
def test_validate_pressure(pres, expected):
    assert validate_pressure(pres) == expected


@pytest.mark.parametrize("value, expected", [
    ("", True),
    ("123", True),
    ("0", True),
    ("11111", True),
    ("abc", False),
    ("12a", False),
    ("1.5", False),
    ("12 34", False),
    ("-1", False),
    ("!", False),
    ("@", False),
    (".", False)
])
def test_only_digits(value, expected):
    assert only_digits(value) == expected
