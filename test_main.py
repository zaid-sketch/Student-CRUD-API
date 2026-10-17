
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


def test_update_student():
    response = client.post("/students", json={
        "name": "Rahul Sharma",
        "date_of_birth": "2003-05-15",
        "email": "rahul@example.com",
        "phone": "9876543210"
    })
    assert response.status_code == 201
    student_id = response.json()["student_id"]

    response = client.put(f"/students/{student_id}", json={
        "name": "Rahul Sharma Updated",
        "date_of_birth": "2003-05-15",
        "email": "rahul.updated@example.com",
        "phone": "9876543210"
    })

    assert response.status_code == 200
    assert response.json()["name"] == "Rahul Sharma Updated"
    assert response.json()["email"] == "rahul.updated@example.com"


def test_update_student_not_found():
    response = client.put("/students/999999999", json={
        "name": "Test Student",
        "date_of_birth": "2003-05-15",
        "email": "test@example.com",
        "phone": "9876543210"
    })

    assert response.status_code == 404


def test_delete_student():
    response = client.post("/students", json={
        "name": "Amit Kumar",
        "date_of_birth": "2003-08-20",
        "email": "amit@example.com",
        "phone": "9876543210"
    })
    assert response.status_code == 201
    student_id = response.json()["student_id"]

    response = client.delete(f"/students/{student_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Student deleted successfully"

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 404


def test_delete_student_not_found():
    response = client.delete("/students/999999999")
    assert response.status_code == 404
