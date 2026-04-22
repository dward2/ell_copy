import pytest
from server import app, upload_processing
from mongo import collection, create_patient, append_cpap_data
from mongo import get_patient, reset_db
from server import (
    validate_server_mrn,
    validate_server_rn,
    validate_server_name,
    validate_server_pressure,
    validate_server_cpap_data,
    validate_uploaded_data,
    format_time
)
from datetime import datetime


@pytest.fixture(autouse=True)
def clean_db():
    reset_db()
    yield
    reset_db()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ---------------- VALIDATION ---------------- #

def test_validate_server_mrn():
    assert validate_server_mrn(123) is True
    assert validate_server_mrn("abc") == "MRN must be an integer"


def test_validate_server_rn():
    assert validate_server_rn("101") is True
    assert validate_server_rn(101) == "Room number must be a string"


def test_validate_server_name():
    assert validate_server_name("Nika") is True
    assert validate_server_name("John123") == \
        "Name contains invalid characters"


def test_validate_server_pressure():
    assert validate_server_pressure(10) is True
    assert validate_server_pressure(3) == \
        "CPAP pressure must be between 4 and 25"


def test_validate_server_cpap_data():
    assert validate_server_cpap_data(20, 2) is True
    assert validate_server_cpap_data("abc", 2) == \
        "Breathing rate must be an integer"


def test_upload_processing_new_patient():
    upload_processing({"mrn": 1, "room_number": "101"})
    patient = get_patient("101")

    assert patient["mrn"] == 1
    assert patient["room_number"] == "101"


def test_upload_processing_replace_patient():
    create_patient(1, "101")
    upload_processing({"mrn": 2, "room_number": "101"})

    patient = get_patient("101")
    assert patient["mrn"] == 2


def test_upload_processing_update_name():
    create_patient(1, "101", "Old")
    upload_processing({"mrn": 1, "room_number": "101", "name": "New"})

    patient = get_patient("101")
    assert patient["name"] == "New"


def test_upload_processing_pressure():
    create_patient(1, "101")
    upload_processing({"mrn": 1, "room_number": "101", "cpap_pressure": 12})

    patient = get_patient("101")
    assert patient["pressure"] == 12


def test_upload_processing_cpap():
    create_patient(1, "101")

    upload_processing({
        "mrn": 1,
        "room_number": "101",
        "breathing_rate": 20,
        "apnea_count": 2,
        "image": "img"
    })

    patient = get_patient("101")

    assert len(patient["cpap_data"]) == 1
    assert patient["breathing_rate"] == 20
    assert patient["apnea_count"] == 2


def test_upload_processing_cpap_append():
    create_patient(1, "101")

    upload_processing({
        "mrn": 1,
        "room_number": "101",
        "breathing_rate": 20,
        "apnea_count": 2,
        "image": "img1"
    })

    upload_processing({
        "mrn": 1,
        "room_number": "101",
        "breathing_rate": 25,
        "apnea_count": 3,
        "image": "img2"
    })

    patient = get_patient("101")

    assert len(patient["cpap_data"]) == 2
    assert patient["cpap_data"][-1]["image"] == "img2"


def test_server_status(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.data.decode() == "server is running"


def test_upload_patient_route(client):
    r = client.post("/api/patient", json={"mrn": 1, "room_number": "101"})
    assert r.status_code == 200


def test_get_rooms(client):
    create_patient(1, "101")
    create_patient(2, "102")

    r = client.get("/rooms")
    data = r.get_json()

    assert set(data) == {"101", "102"}


def test_get_patient_data_from_room(client):
    create_patient(1, "101", "Nika")

    t = datetime.now()
    append_cpap_data("101", 2, 20, "img", t)

    r = client.get("/patient/101")
    data = r.get_json()

    assert data["name"] == "Nika"
    assert data["mrn"] == 1
    assert data["br"] == 20
    assert data["apnea"] == 2

    # fix datetime comparison
    assert data["times"][0] == t.strftime("%m/%d/%y %H:%M:%S")


def test_get_patient_not_found(client):
    r = client.get("/patient/999")
    assert r.status_code == 400


def test_new_pressure(client):
    create_patient(1, "101")

    r = client.post("/pressure", json={"room": "101", "pressure": 10})
    assert r.status_code == 200

    patient = get_patient("101")
    assert patient["pressure"] == 10


def test_new_pressure_invalid(client):
    create_patient(1, "101")

    r = client.post("/pressure", json={"room": "101", "pressure": 100})
    assert r.status_code == 400


def test_get_pressure_not_found(client):
    r = client.get("/pressure?room=999")
    assert r.status_code == 404


def test_format_time():
    dt = datetime(2025, 1, 5, 4, 3, 2)
    assert format_time(dt) == "01/05/25 04:03:02"


def test_patient_moves_rooms():
    create_patient(1, "101")

    upload_processing({"mrn": 1, "room_number": "102"})

    # now two rooms exist
    p1 = get_patient("101")
    p2 = get_patient("102")

    assert p1["mrn"] == 1
    assert p2["mrn"] == 1


def test_replace_clears_cpap():
    create_patient(1, "101")
    append_cpap_data("101", 2, 20, "img1", datetime.now())

    upload_processing({"mrn": 2, "room_number": "101"})

    patient = get_patient("101")

    assert patient["mrn"] == 2
    assert patient["cpap_data"] == []


def test_cpap_creates_patient():
    upload_processing({
        "mrn": 1,
        "room_number": "101",
        "breathing_rate": 20,
        "apnea_count": 2,
        "image": "img"
    })

    patient = get_patient("101")

    assert patient is not None
    assert len(patient["cpap_data"]) == 1


def test_upload_patient_invalid_cpap(client):
    r = client.post("/api/patient", json={
        "mrn": 1,
        "room_number": "101",
        "image": "img"
    })

    assert r.status_code == 400


def test_get_cpap_no_patient(client):
    r = client.get("/cpap?room=101&time=01/01/25 00:00:00")
    assert r.status_code == 404


def test_get_cpap_no_data(client):
    create_patient(1, "101")

    r = client.get("/cpap?room=101&time=01/01/25 00:00:00")
    assert r.status_code == 400


def test_pressure_no_patient(client):
    r = client.post("/pressure", json={"room": "999", "pressure": 10})
    assert r.status_code == 200  # or 400 depending on desired behavior


def test_idempotent_upload():
    data = {"mrn": 1, "room_number": "101"}

    upload_processing(data)
    upload_processing(data)

    patient = get_patient("101")
    assert patient["mrn"] == 1
