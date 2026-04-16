import pytest
import patient_gui
from patient_gui import validate_name


@pytest.mark.parametrize("name", "expected", [
    ("Nika Ilieva", True),
    ("Ella Fortenbery", True),
    (" Nika Ilieva ", True),
    ("", "Please enter a patient name."),
    ("  ","Please enter a patient name."),
    ("John123", "Invalid Name"),
    ("John@Carter", "Invalid Name"),
])
def test_validate_name(name, expected):
    assert name_enter == expected
