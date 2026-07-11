from services.model_service import ModelService
from config.database import get_connection

service = ModelService()
models = service.scan()

conn = get_connection()
cursor = conn.cursor()

# Clear existing records
cursor.execute("DELETE FROM models")

sql = (
    "INSERT OR REPLACE INTO models "
    "(name, model_type, folder, path, size_mb, last_modified) "
    "VALUES (?, ?, ?, ?, ?, ?)"
)

for m in models:
    cursor.execute(
        sql,
        (
            m["name"],
            m["type"],
            m["folder"],
            m["path"],
            m["size"],
            ""
        )
    )

conn.commit()

cursor.execute(
    "SELECT id, name, model_type, size_mb FROM models ORDER BY model_type, name"
)

rows = cursor.fetchall()

print()
print("Models Indexed:", len(rows))
print()

for row in rows:
    print(dict(row))

conn.close()
