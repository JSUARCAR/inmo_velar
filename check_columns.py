import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="db_inmo_velar",
    user="postgres", password="7323"
)
cur = conn.cursor()

# Full columns list
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns
    WHERE table_name = 'recaudos'
    ORDER BY ordinal_position
""")

print("RECAUDOS_ALL_COLUMNS:")
for row in cur.fetchall():
    print(row[0])

# Check if PERIODO exists
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns
    WHERE table_name = 'recaudos' AND column_name = 'periodo'
""")

if cur.fetchone():
    print("\nPERIODO: EXISTS")
else:
    print("\nPERIODO: NOT_EXISTS")

cur.close()
conn.close()
