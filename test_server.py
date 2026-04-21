import pytest
from server import app
from mongo import collection, create_patient, create_patient_cpap, reset_db
from server import validate_server_mrn
from server import validate_server_rn
from server import validate_server_name
from server import validate_server_pressure
from server import validate_server_cpap_data
from server import validate_uploaded_data
from server import get_rooms, get_patient_data_from_room


@pytest.fixture(autouse=True)
def clean_db():
    collection.delete_many({})
    yield
    collection.delete_many({})


@pytest.mark.parametrize("mrn, expected", [
    (123, True),
    (0, True),
    ("abc", "MRN must be an integer"),
    ("123", "MRN must be an integer"),
    (12.5, "MRN must be an integer"),
    (None, "MRN must be an integer"),
    ("123!", "MRN must be an integer"),
])
def test_validate_server_mrn(mrn, expected):
    assert validate_server_mrn(mrn) == expected


@pytest.mark.parametrize("rn, expected", [
    ("101", True),
    ("1", True),
    (101, "Room number must be a string"),
    ("abc", "Room number must contain only digits"),
    ("13a", "Room number must contain only digits"),
    ("17.5", "Room number must contain only digits"),
    (None, "Room number must be a string"),
    (12.5, "Room number must be a string"),
])
def test_validate_server_rn(rn, expected):
    assert validate_server_rn(rn) == expected


@pytest.mark.parametrize("name, expected", [
    ("Nika Ilieva", True),
    ("Ella Fortenbery", True),
    ("Mary-Jane", True),
    (" Nika Ilieva ", True),
    ("", True),
    ("   ", True),
    (123, "Name must be a string"),
    (None, "Name must be a string"),
    ("John123", "Name contains invalid characters"),
    ("John@Carter", "Name contains invalid characters"),
])
def test_validate_server_name(name, expected):
    assert validate_server_name(name) == expected


@pytest.mark.parametrize("pres, expected", [
    (4, True),
    (15, True),
    (25, True),
    ("abc", "CPAP pressure must be an integer"),
    ("10", "CPAP pressure must be an integer"),
    (12.5, "CPAP pressure must be an integer"),
    (None, "CPAP pressure must be an integer"),
    (3, "CPAP pressure must be between 4 and 25"),
    (26, "CPAP pressure must be between 4 and 25"),
    (0, "CPAP pressure must be between 4 and 25"),
])
def test_validate_server_pressure(pres, expected):
    assert validate_server_pressure(pres) == expected


@pytest.mark.parametrize("br, apnea, expected", [
    (21, 3, True),
    (18, 0, True),
    (15, 1, True),
    ("abc", 3, "Breathing rate must be an integer"),
    (12.5, 3, "Breathing rate must be an integer"),
    (None, 3, "Breathing rate must be an integer"),
    (21, "abc", "Apnea count must be an integer"),
    (21, 12.5, "Apnea count must be an integer"),
    (21, None, "Apnea count must be an integer"),
    (-1, 3, "Breathing rate cannot be negative"),
    (21, -1, "Apnea count cannot be negative"),
])
def test_validate_server_cpap_data(br, apnea, expected):
    assert validate_server_cpap_data(br, apnea) == expected


# !!!
@pytest.mark.parametrize("data, expected", [
    ({"mrn": 123, "room_number": "101"}, True),
    ({"mrn": 123, "room_number": "101", "name": "Ella"}, True),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10,
      "breathing_rate": 21, "apnea_count": 3}, True),
    ("not a dict", "Invalid data format"),
    ({}, "MRN is required"),
    ({"mrn": 123}, "Room number is required"),
    ({"mrn": "abc", "room_number": "101"},
     "MRN must be an integer"),
    ({"mrn": 123, "room_number": 101},
     "Room number must be a string"),
    ({"mrn": 123, "room_number": "abc"},
     "Room number must contain only digits"),
    ({"mrn": 123, "room_number": "101", "name": 123},
     "Name must be a string"),
    ({"mrn": 123, "room_number": "101", "name": "John123"},
     "Name contains invalid characters"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": "abc"},
     "CPAP pressure must be an integer"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 3},
     "CPAP pressure must be between 4 and 25"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 26},
     "CPAP pressure must be between 4 and 25"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10},
     "Breathing rate required with CPAP pressure"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10,
      "breathing_rate": 21},
     "Apnea count required with CPAP pressure"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10,
      "breathing_rate": "abc", "apnea_count": 3},
     "Breathing rate must be an integer"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10,
      "breathing_rate": 21, "apnea_count": "abc"},
     "Apnea count must be an integer"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10,
      "breathing_rate": -1, "apnea_count": 3},
     "Breathing rate cannot be negative"),
    ({"mrn": 123, "room_number": "101", "cpap_pressure": 10,
      "breathing_rate": 21, "apnea_count": -1},
     "Apnea count cannot be negative"),
])
def test_validate_upload_data(data, expected):
    assert validate_uploaded_data(data) == expected


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_server_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.decode() == "server is running"


def test_encode_image():
    from server import encode_image
    with open("test_image.jpg", "rb") as image_file:
        b64str = encode_image(image_file)
    assert b64str[0:20] == "/9j/4AAQSkZJRgABAQEA"


def test_decode_image():
    from server import encode_image
    from server import decode_image
    import filecmp
    import os
    with open("test_image.jpg", "rb") as image_file:
        b64str = encode_image(image_file)
    decode_image(b64str, "test_image_output.jpg")
    answer = filecmp.cmp("test_image.jpg",
                         "test_image_output.jpg")
    os.remove("test_image_output.jpg")
    assert answer is True


def test_upload_processing():
    from server import upload_processing
    data = {
        "mrn": 123,
        "room_number": "302"
    }
    message, status = upload_processing(data)
    assert status == 200
    patient = collection.find_one({"mrn": 123})
    assert patient is not None
    assert patient["room_number"] == "302"


def test_upload_processing_w_name():
    from server import upload_processing
    data = {
        "mrn": 123,
        "room_number": "302",
        "name": "Nika"
    }
    message, status = upload_processing(data)
    assert status == 200
    patient = collection.find_one({"mrn": 123})
    assert patient is not None
    assert patient["room_number"] == "302"
    assert patient["name"] == "Nika"


def test_upload_processing_cpap():
    from server import upload_processing
    data = {
        "mrn": 304,
        "room_number": "203",
        "cpap_pressure": 10,
        "breathing_rate": 21,
        "apnea_count": 3
    }
    message, status = upload_processing(data)
    assert status == 200
    patient = collection.find_one({"mrn": 304})
    assert patient is not None
    assert patient["room_number"] == "203"
    assert patient["name"] == "Nika"
    assert len(patient["cpap_data"]) == 1
    assert patient["pressure"] == 10
    assert patient["breathing_rate"] == 21
    assert patient["apnea_count"] == 3


def test_upload_processing_cpap():
    from server import upload_processing
    data = {
        "mrn": 304,
        "room_number": "203",
        "cpap_pressure": 10,
        "breathing_rate": 21,
        "apnea_count": 3,
        "name": "Nika"
    }
    message, status = upload_processing(data)
    assert status == 200
    patient = collection.find_one({"mrn": 304})
    assert patient is not None
    assert patient["room_number"] == "203"
    assert patient["name"] == "Nika"
    assert len(patient["cpap_data"]) == 1
    assert patient["pressure"] == 10
    assert patient["breathing_rate"] == 21
    assert patient["apnea_count"] == 3


def test_upload_patient_route_success(client):
    data = {"mrn": 123, "room_number": "101"}
    r = client.post("/api/patient", json=data)
    assert r.status_code == 200


def test_get_rooms_route(client):
    # setup: clear + insert test data
    reset_db()
    create_patient('123', '101', 'ella',)
    create_patient('456', 'B202', 'nika')
    # call route
    response = client.get("/rooms")
    assert response.status_code == 200
    data = response.get_json()
    assert set(data) == {"101", "B202"}


def test_get_patient_data_from_room_success(client):
    reset_db()
    create_patient_cpap(123, '101', 10, 2, 18, '', 4, 'Nika')

    # call route
    response = client.get("/patient/101")

    # assertions
    assert response.status_code == 200

    data = response.get_json()
    assert data == {
        "name": "Nika",
        "mrn": 123,
        "pressure": 10,
        "br": 18,
        "apnea": 2,
        "times": [4]
    }


def test_get_patient_data_from_room_not_found(client):
    reset_db()
    response = client.get("/patient/Z999")
    assert response.status_code == 400
    assert response.data.decode() == "no patient in room"
