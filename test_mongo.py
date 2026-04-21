import pytest
from pymongo import MongoClient
from mongo import create_patient, create_patient_cpap, update_patient_name
from mongo import update_cpap_data, get_room_list, get_patient, change_pressure
from datetime import datetime

uri = "mongodb+srv://emf55:qFYD@cluster0.tjtcig3.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
client.admin.command({'ping': 1})
db = client["patient_db"]          # creates it if it doesn't exist
collection = db["patient"]


@pytest.fixture(autouse=True)
def clean_db():
    collection.delete_many({})
    yield
    collection.delete_many({})


def test_create_patient():
    create_patient(30, "101")
    patient = collection.find_one({"mrn": 30})
    assert patient is not None
    assert patient["mrn"] == 30
    assert patient["room_number"] == "101"


def test_create_patient_cpap():
    create_patient_cpap(
        200, "302", 10, 3, 21,
        "base64_image",
        "2026-04-21 14:00:00",
        name="Nika"
    )
    patient = collection.find_one({"mrn": 200})
    assert patient["name"] == "Nika"
    assert patient["room_number"] == "302"
    assert len(patient["cpap_data"]) == 1
    assert patient["pressure"] == 10
    assert patient["apnea_count"] == 3
    assert patient["breathing_rate"] == 21


def test_patient_cpap_no_name():
    create_patient_cpap(
        200, "302", 10, 3, 21,
        "base64_image",
        "2026-04-21 14:00:00",
        name=None
    )
    patient = collection.find_one({"mrn": 200})
    assert len(patient["cpap_data"]) == 1
    assert patient["name"] is None
    assert patient["pressure"] == 10
    assert patient["apnea_count"] == 3
    assert patient["breathing_rate"] == 21


def test_update_patient_name():
    create_patient(321, "423", name=None)
    update_patient_name(321, "Nika")
    patient = collection.find_one({"mrn": 321})
    assert patient["name"] == "Nika"


def test_update_patient_name_cpap():
    create_patient_cpap(
        200, "302", 10, 3, 21,
        "base64_image",
        "2026-04-21 14:00:00",
        name=None
    )
    update_patient_name(200, "Nika")
    patient = collection.find_one({"mrn": 200})
    assert patient["name"] == "Nika"


def test_update_patient_name_replacement():
    create_patient(321, "423", name="Ella")
    update_patient_name(321, "Nika")
    patient = collection.find_one({"mrn": 321})
    assert patient["name"] == "Nika"


def test_update_patient_name_replacement_cpap():
    create_patient_cpap(
        200, "302", 10, 3, 21,
        "base64_image",
        "2026-04-21 14:00:00",
        name="Ella"
    )
    update_patient_name(200, "Nika")
    patient = collection.find_one({"mrn": 200})
    assert patient["name"] == "Nika"


def test_patient_name_nonexist():
    update_patient_name(111, "Nika")
    patient = collection.find_one({"mrn": 111})
    assert patient is None


def test_update_cpap_data():
    create_patient(302, "101")
    update_cpap_data(302, 10, 3, 21, "image1",
                     "2026-04-21 14:00:00")
    patient = collection.find_one({"mrn": 302})
    assert patient["pressure"] == 10
    assert patient["apnea_count"] == 3
    assert patient["breathing_rate"] == 21
    assert len(patient["cpap_data"]) == 1
    assert patient["cpap_data"][0]["time"] == "2026-04-21 14:00:00"
    assert patient["cpap_data"][0]["image"] == "image1"


def test_update_cpap_data_appends_history():
    create_patient(302, "101")

    t1 = datetime(2026, 4, 21, 14, 0)
    t2 = datetime(2026, 4, 21, 15, 0)
    t3 = datetime(2026, 4, 21, 16, 0)

    update_cpap_data(302, 10, 3, 21, "image1", t1)
    update_cpap_data(302, 15, 0, 18, "image2", t2)
    update_cpap_data(302, 20, 1, 16, "image3", t3)

    patient = collection.find_one({"mrn": 302})

    times = [e["time"] for e in patient["cpap_data"]]

    assert len(times) == 3
    assert times == sorted(times)
    assert times[0] == t1
    assert times[1] == t2
    assert times[2] == t3


def test_get_room_list():
    collection.delete_many({})  # clean slate

    collection.insert_many([
        {"mrn": 1, "room_number": "A101"},
        {"mrn": 2, "room_number": "B202"},
        {"mrn": 3, "room_number": "A101"},
    ])

    rooms = get_room_list()

    assert set(rooms) == {"A101", "B202"}


def test_get_room_list_empty():
    # ensure collection is empty
    collection.delete_many({})
    rooms = get_room_list()
    assert rooms == []


def test_get_patient():
    collection.delete_many({})  # clean state
    collection.insert_one({
        "mrn": 123,
        "name": "Nika",
        "room_number": "A101"
    })
    patient = get_patient("A101")
    assert patient is not None
    assert patient["mrn"] == 123
    assert patient["name"] == "Nika"
    assert patient["room_number"] == "A101"


def test_get_patient_not_found():
    collection.delete_many({})  # ensure empty
    patient = get_patient("Z999")
    assert patient is None


def test_change_pressure():
    collection.delete_many({})  # clean state

    # setup
    collection.insert_one({
        "mrn": 1,
        "room_number": "A101",
        "pressure": 5
    })

    # call function
    change_pressure("A101", 10)

    # verify
    patient = collection.find_one({"room_number": "A101"})
    assert patient is not None
    assert patient["pressure"] == 10


def test_change_pressure_no_patient():
    collection.delete_many({})
    change_pressure("Z999", 10)
    patient = collection.find_one({"room_number": "Z999"})
    assert patient is None
