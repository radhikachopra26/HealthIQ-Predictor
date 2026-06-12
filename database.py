import hashlib
import sqlite3
from datetime import datetime

DB_NAME = "health_prediction.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            glucose REAL NOT NULL,
            haemoglobin REAL NOT NULL,
            cholesterol REAL NOT NULL,
            remarks TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(full_name, email, phone, password=None):
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password) if password else None

    cursor.execute("""
        INSERT INTO users (full_name, email, phone, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        full_name,
        email,
        phone,
        password_hash,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE phone=?", (phone,))
    user = cursor.fetchone()
    conn.close()
    return user


def verify_password(email, password):
    user = get_user_by_email(email)

    if not user:
        return None

    if user[4] == hash_password(password):
        return user

    return None


def add_record(user_id, full_name, dob, email, glucose, haemoglobin, cholesterol, remarks):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO records 
        (user_id, full_name, dob, email, glucose, haemoglobin, cholesterol, remarks, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_records_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, full_name, dob, email, glucose, haemoglobin, cholesterol, remarks, created_at
        FROM records
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (user_id,))

    records = cursor.fetchall()
    conn.close()
    return records


def update_record(record_id, full_name, dob, email, glucose, haemoglobin, cholesterol, remarks):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE records
        SET full_name=?, dob=?, email=?, glucose=?, haemoglobin=?, cholesterol=?, remarks=?
        WHERE id=?
    """, (
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks,
        record_id
    ))

    conn.commit()
    conn.close()


def delete_record(record_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


def seed_demo_users():
    demo_users = [
        ("Anuj Sharma", "anuj.demo@example.com", "9876543210", "Anuj@123"),
        ("Keshav Mehra", "keshav.demo@example.com", "9876543211", "Keshav@123")
    ]

    for full_name, email, phone, password in demo_users:
        if not get_user_by_email(email):
            create_user(full_name, email, phone, password)