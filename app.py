from flask import Flask, jsonify, request
from database import get_connection, init_db
import mysql.connector

app = Flask(__name__)


# ─── Helper: convert cursor rows to list of dicts ────────────────
def rows_to_list(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


# ════════════════════════════════════════════════════════════════════
# READ ALL   GET /employees
# ════════════════════════════════════════════════════════════════════
@app.route("/employees", methods=["GET"])
def get_all_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = rows_to_list(cursor)
    cursor.close()
    conn.close()

    return jsonify({
        "status":    "success",
        "count":     len(employees),
        "employees": employees
    }), 200


# ════════════════════════════════════════════════════════════════════
# READ ONE   GET /employees/<id>
# ════════════════════════════════════════════════════════════════════
@app.route("/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        return jsonify({
            "status":  "error",
            "message": f"Employee with ID {employee_id} not found"
        }), 404

    employee = row_to_dict(cursor, row)
    cursor.close()
    conn.close()

    return jsonify({
        "status":   "success",
        "employee": employee
    }), 200


# ════════════════════════════════════════════════════════════════════
# CREATE     POST /employees
# ════════════════════════════════════════════════════════════════════
@app.route("/employees", methods=["POST"])
def create_employee():
    data = request.get_json()

    # Validate all required fields
    required_fields = [
        "first_name", "last_name", "email", "phone_number",
        "department", "designation", "salary", "joining_date"
    ]
    missing = [f for f in required_fields if not data or f not in data]
    if missing:
        return jsonify({
            "status":  "error",
            "message": f"Missing required fields: {', '.join(missing)}"
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO employees
                (first_name, last_name, email, phone_number, department, designation, salary, joining_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data["first_name"],
            data["last_name"],
            data["email"],
            data["phone_number"],
            data["department"],
            data["designation"],
            data["salary"],
            data["joining_date"]
        ))
        conn.commit()
        new_id = cursor.lastrowid

    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        return jsonify({
            "status":  "error",
            "message": "Email already exists. Each employee must have a unique email."
        }), 409

    # Return the newly created employee
    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (new_id,))
    row = cursor.fetchone()
    new_employee = row_to_dict(cursor, row)
    cursor.close()
    conn.close()

    return jsonify({
        "status":   "success",
        "message":  "Employee created successfully",
        "employee": new_employee
    }), 201


# ════════════════════════════════════════════════════════════════════
# UPDATE     PUT /employees/<id>
# ════════════════════════════════════════════════════════════════════
@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Check employee exists
    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return jsonify({
            "status":  "error",
            "message": f"Employee with ID {employee_id} not found"
        }), 404

    data = request.get_json()

    allowed_fields = [
        "first_name", "last_name", "email", "phone_number",
        "department", "designation", "salary", "joining_date"
    ]
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        cursor.close()
        conn.close()
        return jsonify({
            "status":  "error",
            "message": "No valid fields provided to update."
        }), 400

    set_clause = ", ".join([f"{col} = %s" for col in updates.keys()])
    values = list(updates.values()) + [employee_id]

    cursor.execute(
        f"UPDATE employees SET {set_clause} WHERE employee_id = %s",
        values
    )
    conn.commit()

    # Return the updated employee
    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
    row = cursor.fetchone()
    updated_employee = row_to_dict(cursor, row)
    cursor.close()
    conn.close()

    return jsonify({
        "status":   "success",
        "message":  "Employee updated successfully",
        "employee": updated_employee
    }), 200


# ════════════════════════════════════════════════════════════════════
# DELETE     DELETE /employees/<id>
# ════════════════════════════════════════════════════════════════════
@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return jsonify({
            "status":  "error",
            "message": f"Employee with ID {employee_id} not found"
        }), 404

    cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status":  "success",
        "message": f"Employee with ID {employee_id} deleted successfully"
    }), 200


# ════════════════════════════════════════════════════════════════════
# Start the app
# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)