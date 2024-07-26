
import jwt

from permissions import get_permissions, SECRET_KEY
from sql_metadata import Parser
from db import SQLiteClient

class AuthZ:
    def __init__(self, db_string):
        self.db_client = SQLiteClient(db_string=db_string)
        self.READ_OPERATIONS = ["select", "where", "order_by", "group_by", "join"]
        self.WRITE_OPERATIONS = ["insert", "update"]

    def auth_execute(self, query, access_token):
        try:
            user_id = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])["user_id"]
        except jwt.exceptions.DecodeError:
            return { "error": "Invalid access token" }

        # Parse tables/columns from query, naively determine read vs. write operation, and pull
        # permissions from the database and transform into a useable format.
        tables = Parser(query).tables
        operation = "write" if any(operation in query for operation in self.WRITE_OPERATIONS) else "read"
        permissions = self.__transform_permissions(get_permissions(user_id=user_id))
        columns = Parser(query).columns_dict

        # Check table-level permissions for each table in the query
        authenticated_tables = []
        table_authenticated = False
        for table in tables:
            if self.__table_permissioned(table=table, permissions=permissions, operation=operation):
                authenticated_tables.append(table)

        # If every table in the query is correctly permissioned, then the query is authenticated
        # and we don't need to check the individual columns
        if set(authenticated_tables) == set(tables):
            table_authenticated = True

        # If not every table in the query is permissioned, then we need to check that the
        # individual columns are.
        if not table_authenticated:
            columns_dict = Parser(query).columns_dict
            table_name = tables[0] if len(tables) == 1 else None
            for section, columns in columns_dict.items():
                formatted_columns = self.__format_columns(columns, table_name=table_name)
                for formatted_column in formatted_columns:
                    # If there is table-level permissions for the column already, we don't
                    # need to check column-level permissions
                    if formatted_column[:formatted_column.find(".")] in authenticated_tables:
                        continue

                    operation = "write" if section in self.WRITE_OPERATIONS else "read"
                    if not self.__column_permissioned(column=formatted_column, permissions=permissions, operation=operation):
                        return {"error": "Access denied"}
                
        self.db_client.open_connection()
        res = self.db_client.execute(query=query)
        self.db_client.commit()
        return list(res.fetchall())

    def __format_columns(self, columns, table_name=None):
        # In the case that there is only one table referenced, the columns might not be
        # prefixed by the table name.
        if table_name:
            columns = [f"{table_name}.{column}" for column in columns]
        
        # If * is used, we need to enumerate every column in that table to check its permissions.
        formatted_columns = []
        for column in columns:
            if "*" not in column:
                formatted_columns.append(column)
            else:
                table = column[:column.find(".")]
                column_names = self.__get_all_columns(table=table)
                column_names = [f"{table}.{column_name}" for column_name in column_names]
                formatted_columns.extend(column_names)
        
        return formatted_columns

    def __get_all_columns(self, table):
        self.db_client.open_connection()
        res = list(self.db_client.execute(f"PRAGMA table_info('{table}')"))
        return [entry[1] for entry in res]

    def __table_permissioned(self, table, permissions, operation):
        if operation == "read":
            if "r" not in permissions.get(table, []) and "rw" not in permissions.get(table, []):
                return False
        elif operation == "write":
            if "rw" not in permissions.get(table, []):
                return False
        else:
            raise Exception("Invalid operation type")
        
        return True
        
    def __column_permissioned(self, column, permissions, operation):
        if operation == "read":
            if "r" not in permissions.get(column, []) and "rw" not in permissions.get(column, []):
                return False
        elif operation == "write":
            if "rw" not in permissions.get(column, []):
                return False
        else:
            raise Exception("Invalid operation type")

        return True

    def __transform_permissions(self, permissions):
        res = {}
        for permission in permissions:
            table = permission["table_name"]
            type = permission["type"]
            column = permission["column"]
            access_level = permission["access_level"]
            if type == "table":
                if res.get(table):
                    res[table].append(access_level)
                else:
                    res[table] = [access_level]
            else:
                if res.get(f"{table}.{column}"):
                    res[f"{table}.{column}"].append(access_level)
                else:
                    res[f"{table}.{column}"] = [access_level]
        return res
