import sqlite3

connection = sqlite3.connect("database/movie_studio.db")

cursor = connection.cursor()

with open("database/schema.sql") as f:
    cursor.executescript(f.read())

connection.commit()

connection.close()

print("Database initialized.")
