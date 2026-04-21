import pytest
from server import app
from mongo import collection
from server import validate_server_mrn
from server import validate_server_rn
from server import validate_server_name
from server import validate_server_pressure


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
    # assert patient["name"] == "Nika"


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
    assert patient["cpap_data"][0]["pressure"] == 10
    assert patient["cpap_data"][0]["breathing_rate"] == 21
    assert patient["cpap_data"][0]["apnea_count"] == 3


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
    assert patient["cpap_data"][0]["pressure"] == 10
    assert patient["cpap_data"][0]["breathing_rate"] == 21
    assert patient["cpap_data"][0]["apnea_count"] == 3


def test_upload_patient_route_success(client):
    data = {"mrn": 123, "room_number": "101"}
    r = client.post("/api/patient", json=data)
    assert r.status_code == 200
