import pytest
import patient_gui
from patient_gui import validate_name
from patient_gui import validate_mrn


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
