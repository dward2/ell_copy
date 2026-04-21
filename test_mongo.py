import pytest
from pymongo import MongoClient
from mongo import create_patient, create_patient_cpap, update_patient_name

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
    assert patient["cpap_data"][0]["pressure"] == 10
    assert patient["cpap_data"][0]["apnea_count"] == 3
    assert patient["cpap_data"][0]["breathing_rate"] == 21


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
    assert patient["cpap_data"][0]["pressure"] == 10
    assert patient["cpap_data"][0]["apnea_count"] == 3
    assert patient["cpap_data"][0]["breathing_rate"] == 21


def test_update_patient_name():
    create_patient(321, "423")
    update_patient_name(321, "Nika")
    patient = collection.find_one({"mrn": 321})
    assert patient["name"] == "Nika"
