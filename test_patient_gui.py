import pytest
import patient_gui
from patient_gui import validate_name
from patient_gui import validate_mrn
from patient_gui import validate_rn
from patient_gui import validate_pressure


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
