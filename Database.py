import mysql.connector
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def get_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id   INT           AUTO_INCREMENT PRIMARY KEY,
            first_name    VARCHAR(50)   NOT NULL,
            last_name     VARCHAR(50)   NOT NULL,
            email         VARCHAR(100)  NOT NULL UNIQUE,
            phone_number  VARCHAR(15)   NOT NULL,
            department    VARCHAR(50)   NOT NULL,
            designation   VARCHAR(100)  NOT NULL,
            salary        DECIMAL(10,2) NOT NULL,
            joining_date  DATE          NOT NULL
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_employees = [
            ("Rahul",  "Sharma", "rahul.sharma@company.com",  "9876543210", "Engineering", "Software Engineer",   75000, "2022-06-15"),
            ("Priya",  "Mehta",  "priya.mehta@company.com",   "9123456789", "HR",           "HR Manager",          65000, "2021-03-01"),
            ("Amit",   "Verma",  "amit.verma@company.com",    "9988776655", "Finance",      "Accountant",          55000, "2023-01-10"),
            ("Sneha",  "Patil",  "sneha.patil@company.com",   "9876501234", "Marketing",    "Marketing Executive", 50000, "2024-02-20"),
            ("Vikram", "Singh",  "vikram.singh@company.com",  "9090909090", "Engineering",  "DevOps Engineer",     80000, "2020-11-05"),
        ]
        cursor.executemany('''
            INSERT INTO employees
                (first_name, last_name, email, phone_number, department, designation, salary, joining_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', sample_employees)
        conn.commit()
        print("Sample data inserted.")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database ready — employees table loaded.")