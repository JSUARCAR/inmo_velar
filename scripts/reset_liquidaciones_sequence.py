"""Script para resetear secuencia de liquidaciones"""
from src.infraestructura.persistencia.database import DatabaseManager

db = DatabaseManager()
conn = db.obtener_conexion()
cursor = db.get_dict_cursor(conn)

print("🔧 Reseteando secuencia de liquidaciones...")

# Obtener MAX ID
cursor.execute("SELECT MAX(id_liquidacion) as max_id FROM liquidaciones")
result = cursor.fetchone()
max_id = result['MAX_ID'] if result and result.get('MAX_ID') is not None else 0

next_val = max_id + 1

# Resetear secuencia
cursor.execute(f"ALTER SEQUENCE liquidaciones_id_liquidacion_seq RESTART WITH {next_val}")
conn.commit()

print(f"✅ Secuencia reseteada correctamente a: {next_val}")
print(f"   MAX ID actual: {max_id}")
print(f"   Próximo ID: {next_val}")

conn.close()
