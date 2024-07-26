import sqlite3
from sqlite3 import Error

class SQLiteDBHelper:
    def __init__(self, db_file):
        """Initialize the SQLiteDBHelper with the database file."""
        self.db_file = db_file
        self.conn = None

    def create_connection(self):
        """Create a database connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Execute a single query."""
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            self.conn.commit()
            return cur.lastrowid
        except Error as e:
            print(f"Error executing query: {e}")

    def execute_read_query(self, query, params=None):
        """Execute a query to read data."""
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            rows = cur.fetchall()
            return rows
        except Error as e:
            print(f"Error reading data: {e}")
            return None

    def create_table(self, create_table_sql):
        """Create a table with the provided SQL statement."""
        try:
            cur = self.conn.cursor()
            cur.execute(create_table_sql)
            self.conn.commit()
        except Error as e:
            print(f"Error creating table: {e}")
