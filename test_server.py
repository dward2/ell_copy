import pytest
from server import app
from mongo import collection


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


'''


def test_upload_patient(client):
    from server import upload_patient
    data = {
        "mrn": 123,
        "room_number": "302"
    }
    r = client.post("/api/patient", json=data)
    assert r.status_code == 200


def test_upload_patient_w_name(client):
    data = {
        "mrn": 321,
        "room_number": "303",
        "name": "Nika"
    }
    r = client.post("/api/patient", json=data)
    assert r.status_code == 200


def test_upload_patient_w_cpap(client):
    data = {
        "mrn": 304,
        "room_number": "203",
        "cpap_pressure": 10,
        "breathing_rate": 21,
        "apnea_count": 3
    }
    r = client.post("/api/patient", json=data)
    assert r.status_code == 200


def test_upload_patient_cpap_w_name(client):
    data = {
        "mrn": 304,
        "room_number": "203",
        "name": "Nika",
        "cpap_pressure": 10,
        "breathing_rate": 21,
        "apnea_count": 3
    }
    r = client.post("/api/patient", json=data)
    assert r.status_code == 200
'''
