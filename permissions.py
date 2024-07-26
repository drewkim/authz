import sqlite3
import jwt
from db import SQLiteClient

SECRET_KEY='super-secret-key'
ACCESS_LEVELS = ["rw", "r"]
TABLE_NAMES = ["posts", "comments", "likes"]
PERMISSION_TYPES = ["table", "column"]

db_client = SQLiteClient(db_string="auth.db")

def create_user(email):
    db_client.open_connection()
    db_client.execute(f"INSERT INTO users (email) VALUES ('{email}')")

    user_id = db_client.cursor.lastrowid
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    print(token)

    try:
        db_client.execute(f"UPDATE users SET access_token = '{token}' WHERE id = {user_id}")
    except sqlite3.IntegrityError:
        return { "error": "Email must be unique" }

    db_client.commit()
    
    return { "user_id": user_id, "token": token }

def set_permission(user_id, table_name, access_level, type, column=None):
    if table_name not in TABLE_NAMES:
        return { "error": "Invalid table name" }
    if access_level not in ACCESS_LEVELS:
        return { "error": "Invalid access level" }
    if type not in PERMISSION_TYPES:
        return { "error": "Invalid permission type" }
    
    db_client.open_connection()
    db_client.execute(f"INSERT INTO permissions (user_id, table_name, access_level, type, column) VALUES ('{user_id}', '{table_name}', '{access_level}', '{type}', '{column}')")
    db_client.commit()
    permission_id = db_client.cursor.lastrowid

    return { "permission_id": permission_id }

def get_permissions(user_id, table_name=None, type=None, column=None):
    db_client.open_connection()
    query_string = f"SELECT * FROM permissions WHERE user_id = {user_id}"

    if table_name:
        query_string += f" AND table_name = '{table_name}'"
    if type:
        query_string += f" AND type = '{type}'"
    if column:
        query_string += f" AND column = '{column}'"
    
    res = db_client.execute(query_string)
    permissions = res.fetchall()

    return [{
        "id": permission[0],
        "user_id": permission[1],
        "table_name": permission[2],
        "access_level": permission[3],
        "type": permission[4],
        "column": permission[5],
    } for permission in permissions]

def clear_permissions(user_id):
    db_client.open_connection()
    db_client.execute(f"DELETE FROM permissions WHERE user_id = {user_id}")
    db_client.commit()
