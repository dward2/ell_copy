import pytest
from pymongo import MongoClient
from mongo import create_patient

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
