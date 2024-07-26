import sqlite3

def init_permissions_db():
    with open("auth_schema.sql") as file:
        connection = sqlite3.connect("auth.db")
        connection.executescript(file.read())
        connection.close()
    
def init_main_db():
    with open("main_schema.sql") as file:
        connection = sqlite3.connect("main.db")
        connection.executescript(file.read())
        connection.close()

init_permissions_db()
init_main_db()
