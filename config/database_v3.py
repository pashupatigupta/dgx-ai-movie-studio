"""
SQLite Database Manager
"""

import sqlite3


DATABASE = "database/movie_studio.db"


def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn

