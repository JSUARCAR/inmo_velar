import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="inmo_user",
    password="7323"
)

cursor = conn.cursor()

# Check codeudor 35 specifically
print("===== Checking Codeudor ID 35 =====")
cursor.execute("""
    SELECT C.ID_CODEUDOR, C.ID_PERSONA, C.ESTADO_REGISTRO,
           P.NOMBRE_COMPLETO, P.NUMERO_DOCUMENTO, P.ESTADO_REGISTRO as PERSONA_ACTIVA
    FROM CODEUDORES C
    LEFT JOIN PERSONAS P ON C.ID_PERSONA = P.ID_PERSONA
    WHERE C.ID_CODEUDOR = 35
""")
row = cursor.fetchone()
if row:
    print(f"Codeudor exists:")
    print(f"  ID_CODEUDOR: {row[0]}")
    print(f"  ID_PERSONA: {row[1]}")
    print(f"  CODEUDOR.ESTADO_REGISTRO: {row[2]}")
    print(f"  PERSONA.NOMBRE_COMPLETO: {row[3]}")
    print(f"  PERSONA.NUMERO_DOCUMENTO: {row[4]}")
    print(f"  PERSONA.ESTADO_REGISTRO: {row[5]}")
    
    # Explain why it's being filtered out
    if not row[2]:
        print("\n❌ FILTERED OUT: Codeudor ESTADO_REGISTRO is FALSE")
    elif not row[5]:
        print("\n❌ FILTERED OUT: Persona ESTADO_REGISTRO is FALSE")
    else:
        print("\n✅ Should be INCLUDED in the list!")
else:
    print("Codeudor ID 35 does not exist!")

cursor.close()
conn.close()
