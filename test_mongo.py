import pytest
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from mongo import (
    collection,
    create_patient,
    replace_patient_in_room,
    update_patient_name,
    append_cpap_data,
    get_room_list,
    get_patient,
    change_pressure,
    reset_db
)


@pytest.fixture(autouse=True)
def clean_db():
    reset_db()
    yield
    reset_db()


def test_create_patient():
    create_patient(123, "101", "Nika")

    patient = collection.find_one({"room_number": "101"})

    assert patient is not None
    assert patient["mrn"] == 123
    assert patient["name"] == "Nika"
    assert patient["pressure"] is None
    assert patient["apnea_count"] is None
    assert patient["breathing_rate"] is None
    assert patient["cpap_data"] == []


def test_room_unique():
    create_patient(123, "101")

    with pytest.raises(DuplicateKeyError):
        create_patient(456, "101")


def test_replace_patient_in_room():
    create_patient(123, "101", "Old")

    replace_patient_in_room(456, "101", "New")

    patients = list(collection.find({"room_number": "101"}))
    assert len(patients) == 1
    assert patients[0]["mrn"] == 456
    assert patients[0]["name"] == "New"
    assert patients[0]["cpap_data"] == []


def test_update_patient_name():
    create_patient(123, "101", "Old")

    update_patient_name("101", "New")

    patient = get_patient("101")
    assert patient["name"] == "New"


def test_change_pressure():
    create_patient(123, "101")

    change_pressure("101", 10)

    patient = get_patient("101")
    assert patient["pressure"] == 10


def test_append_cpap_data():
    create_patient(123, "101")

    t1 = datetime.now()
    append_cpap_data("101", 2, 18, "img1", t1)

    patient = get_patient("101")

    assert patient["apnea_count"] == 2
    assert patient["breathing_rate"] == 18
    assert len(patient["cpap_data"]) == 1
    assert patient["cpap_data"][0]["image"] == "img1"
    assert patient["cpap_data"][0]["time"].strftime("%m/%d/%y %H:%M:%S") == \
        t1.strftime("%m/%d/%y %H:%M:%S")


def test_append_cpap_data_multiple():
    create_patient(123, "101")

    t1 = datetime.now()
    t2 = datetime.now()

    append_cpap_data("101", 2, 18, "img1", t1)
    append_cpap_data("101", 3, 20, "img2", t2)

    patient = get_patient("101")

    assert len(patient["cpap_data"]) == 2
    assert patient["cpap_data"][0]["image"] == "img1"
    assert patient["cpap_data"][1]["image"] == "img2"

    # latest values overwrite
    assert patient["apnea_count"] == 3
    assert patient["breathing_rate"] == 20


def test_get_room_list():
    create_patient(1, "101")
    create_patient(2, "102")

    rooms = get_room_list()

    assert set(rooms) == {"101", "102"}


def test_get_patient():
    create_patient(123, "101")

    patient = get_patient("101")

    assert patient is not None
    assert patient["mrn"] == 123


def test_get_patient_not_found():
    patient = get_patient("999")
    assert patient is None
