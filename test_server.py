import pytest
from server import app


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


