from datetime import date
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator, model_validator

DATABASE = "students.db"

app = FastAPI(title="Student CRUD API")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        """)


create_table()

class StudentCreate(BaseModel):
    name: str
    date_of_birth: date
    email: EmailStr | None = None
    phone: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Student name cannot be empty")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is not None:
            if not value.isascii() or not value.isdigit() or len(value) != 10:
                raise ValueError("Phone number must contain exactly 10 digits")
        return value

    @model_validator(mode="after")
    def check_contact(self):
        if not self.email and not self.phone:
            raise ValueError("Enter at least an email or a phone number")
        return self


class Student(StudentCreate):
    student_id: int


@app.get("/")
def home():
    return {"message": "Student CRUD API is running"}


@app.post("/students", response_model=Student, status_code=201)
def create_student(student: StudentCreate):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO students (name, date_of_birth, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (
                student.name,
                student.date_of_birth.isoformat(),
                student.email,
                student.phone,
            ),
        )
        student_id = cursor.lastrowid

    return get_student(student_id)


@app.get("/students", response_model=list[Student])
def list_students(search: str | None = None):
    with get_connection() as connection:
        if search:
            rows = connection.execute(
                "SELECT * FROM students WHERE name LIKE ? ORDER BY student_id",
                (f"%{search}%",),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM students ORDER BY student_id"
            ).fetchall()

    return [dict(row) for row in rows]


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return dict(row)


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentCreate):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE students
            SET name = ?, date_of_birth = ?, email = ?, phone = ?
            WHERE student_id = ?
            """,
            (
                student.name,
                student.date_of_birth.isoformat(),
                student.email,
                student.phone,
                student_id,
            ),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

    return get_student(student_id)


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE student_id = ?",
            (student_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}