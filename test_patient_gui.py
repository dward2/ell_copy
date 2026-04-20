import pytest
import patient_gui
from patient_gui import validate_name
from patient_gui import validate_mrn
from patient_gui import validate_rn
from patient_gui import validate_pressure
from patient_gui import only_digits
from patient_gui import check_required_fields
from patient_gui import apnea_color


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


@pytest.mark.parametrize("mrn, rn, expected", [
    ("123", "101", []),
    ("", "101", ["Please enter Medical Record Number"]),
    ("123", "", ["Please enter Room Number"]),
    ("", "", ["Please enter Medical Record Number",
              "Please enter Room Number"]),
    ("abc", "101", ["MRN Invalid"]),
    ("123", "abc", ["Room Number Invalid"]),
    ("abc", "xyz", ["MRN Invalid", "Room Number Invalid"]),
])
def test_check_required_fields(mrn, rn, expected):
    assert check_required_fields(mrn, rn) == expected


@pytest.mark.parametrize("count, expected", [
    (0, "white"),
    (1, "white"),
    (2, "red"),
    (3, "red"),
    (10, "red"),
])
def test_apnea_color(count, expected):
    assert apnea_color(count) == expected
