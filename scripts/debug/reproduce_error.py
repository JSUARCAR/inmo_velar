import sqlite3

# Test 1: Simple select with alias
query1 = "SELECT m.ID_PROPIETARIO FROM CONTRATOS_MANDATOS m LIMIT 1"

# Test 2: Simple select without alias
query2 = "SELECT ID_PROPIETARIO FROM CONTRATOS_MANDATOS LIMIT 1"

conn = sqlite3.connect('DB_Inmo_Velar.db')
cursor = conn.cursor()

print("--- Test 1 (with alias) ---")
try:
    cursor.execute(query1)
    print("Success")
except Exception as e:
    print("Failed:", e)

print("\n--- Test 2 (without alias) ---")
try:
    cursor.execute(query2)
    print("Success")
except Exception as e:
    print("Failed:", e)

conn.close()
