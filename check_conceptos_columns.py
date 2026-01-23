import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="db_inmo_velar",
    user="postgres", password="7323"
)
cur = conn.cursor()

# Get recaudo_conceptos columns
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns
    WHERE table_name = 'recaudo_conceptos'
    ORDER BY ordinal_position
""")

print("RECAUDO_CONCEPTOS_COLUMNS:")
for row in cur.fetchall():
    print(row[0])

cur.close()
conn.close()
