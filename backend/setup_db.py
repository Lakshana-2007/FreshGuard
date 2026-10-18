import psycopg2
import os

conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="laks9344773283",
    dbname="freshness_db"
)
conn.autocommit = True
cur = conn.cursor()

schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
with open(schema_path, 'r') as f:
    schema = f.read()

cur.execute(schema)
print("Schema applied successfully!")

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
tables = cur.fetchall()
print("Tables in freshness_db:", [t[0] for t in tables])

cur.close()
conn.close()
