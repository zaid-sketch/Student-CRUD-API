
import os
import tempfile

# Use a separate database so tests do not modify real student data.
test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
test_db.close()
os.environ["STUDENT_DATABASE"] = test_db.name

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Student CRUD API is running"


def test_create_student():
    response = client.post("/students", json={
        "name": "Amit Kumar",
        "date_of_birth": "2003-08-20",
        "email": "amit@example.com",
        "phone": "9876543210"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Amit Kumar"


def test_get_students():
    response = client.get("/students")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_phone():
    response = client.post("/students", json={
        "name": "Rahul",
        "date_of_birth": "2003-08-20",
        "email": "rahul@example.com",
        "phone": "123"
    })
    assert response.status_code == 422


def test_invalid_email():
    response = client.post("/students", json={
        "name": "Rahul",
        "date_of_birth": "2003-08-20",
        "email": "invalid-email",
        "phone": "9876543210"
    })
    assert response.status_code == 422


def test_student_not_found():
    response = client.get("/students/999999")
    assert response.status_code == 404
