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
