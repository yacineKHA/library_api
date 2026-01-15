import sqlite3

DB = "library.db"

with open("schema.sql", "r") as f:
    schema = f.read()

conn = sqlite3.connect(DB)
conn.executescript(schema)
conn.commit()
conn.close()

print("Bdd créée avec succès.")