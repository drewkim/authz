import sqlite3
from abc import ABC, abstractmethod

class DBClient(ABC):
    def __init__(self, db_string):
        self.db_string = db_string

    @abstractmethod
    def open_connection(self):
        pass

    @abstractmethod
    def execute(self, query):
        pass
    
    @abstractmethod
    def close_connection(self):
        pass

    @abstractmethod
    def commit(self):
        pass

class SQLiteClient(DBClient):
    def open_connection(self):
        self.connection = sqlite3.connect(self.db_string)
        self.cursor = self.connection.cursor()

    def execute(self, query):
        return self.cursor.execute(query)
    
    def close_connection(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()
