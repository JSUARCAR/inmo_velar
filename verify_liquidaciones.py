"""Script para verificar estado de liquidaciones y secuencia"""
from src.infraestructura.persistencia.database import DatabaseManager

db = DatabaseManager()
conn = db.obtener_conexion()
# Usar el método del DatabaseManager para obtener dict cursor
cursor = db.get_dict_cursor(conn)

print("=" * 60)
print("VERIFICACIÓN DE LIQUIDACIONES Y SECUENCIA")
print("=" * 60)

# Verificar liquid aciones existentes (CursorWrapper uppercases keys)
cursor.execute("SELECT COUNT(*) as total FROM liquidaciones")
result = cursor.fetchone()
total = result['TOTAL'] if result else 0
print(f"\n✓ Total liquidaciones en BD: {total}")

# Verificar MAX ID
cursor.execute("SELECT MAX(id_liquidacion) as max_id FROM liquidaciones")
result = cursor.fetchone()
max_id = result['MAX_ID'] if result and result.get('MAX_ID') is not None else 0
print(f"✓ MAX ID en tabla: {max_id}")

# Verificar secuencia
try:
    cursor.execute("SELECT last_value FROM liquidaciones_id_liquidacion_seq")
    result = cursor.fetchone()
    seq_val = result['LAST_VALUE']
    print(f"✓ Valor actual de secuencia: {seq_val}")
    
    if seq_val <= max_id:
        print(f"\n⚠️  PROBLEMA: Secuencia desincronizada!")
        print(f"   Secuencia ({seq_val}) <= MAX ID ({max_id})")
        print(f"   Esto causará error de clave duplicada")
    else:
        print(f"\n✓ Secuencia OK (mayor que MAX ID)")
except Exception as e:
    print(f"\n⚠️  Error verificando secuencia: {e}")

# Verificar liquidaciones de enero 2026
cursor.execute("SELECT id_liquidacion, id_contrato_m, periodo FROM liquidaciones WHERE periodo LIKE '%enero%2026%' ORDER BY id_liquidacion")
enero_liq = cursor.fetchall()
print(f"\n✓ Liquidaciones de 'enero de 2026': {len(enero_liq)}")
for liq in enero_liq:
    print(f"   - ID: {liq['ID_LIQUIDACION']}, Contrato: {liq['ID_CONTRATO_M']}, Periodo: {liq['PERIODO']}")

# Verificar últimas 5 liquidaciones
cursor.execute("SELECT id_liquidacion, periodo FROM liquidaciones ORDER BY id_liquidacion DESC LIMIT 5")
ultimas = cursor.fetchall()
print(f"\n✓ Últimas 5 liquidaciones:")
for liq in ultimas:
    print(f"   - ID: {liq['ID_LIQUIDACION']}, Periodo: {liq['PERIODO']}")

print("\n" + "=" * 60)

conn.close()
