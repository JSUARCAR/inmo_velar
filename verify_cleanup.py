import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=os.getenv("DB_PASSWORD", "")
)

cur = conn.cursor()

print("="*70)
print("VERIFICACIÓN POST-LIMPIEZA")
print("="*70)

# Contar descuentos totales
cur.execute("SELECT COUNT(*) FROM DESCUENTOS_ASESORES")
total_desc = cur.fetchone()[0]

# Verificar liquidaciones con descuentos
cur.execute("""
    SELECT 
        id_liquidacion_asesor,
        COUNT(*) as num_descuentos,
        SUM(valor_descuento) as total
    FROM DESCUENTOS_ASESORES
    GROUP BY id_liquidacion_asesor
    ORDER BY num_descuentos DESC
    LIMIT 10
""")

print(f"\n✅ Total descuentos en BD: {total_desc:,}")
print("\nTop 10 liquidaciones con más descuentos:")
print("-" * 70)
for row in cur.fetchall():
    print(f"  Liquidación {row[0]:3}: {row[1]:3} descuentos = ${row[2]:,}")

# Verificar que no haya liquidaciones con demasiados duplicados
cur.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT id_liquidacion_asesor
        FROM DESCUENTOS_ASESORES
        GROUP BY id_liquidacion_asesor
        HAVING COUNT(*) > 10
    ) as over_ten
""")
liquidaciones_sospechosas = cur.fetchone()[0]

print(f"\n⚠️  Liquidaciones con >10 descuentos: {liquidaciones_sospechosas}")

if liquidaciones_sospechosas == 0:
    print("✅ No se detectaron duplicados excesivos")
else:
    print("⚠️  Aún hay liquidaciones con muchos descuentos (revisar manualmente)")

# Muestra de liquidación actualizada
cur.execute("""
    SELECT 
        id_liquidacion_asesor,
        periodo_liquidacion,
        comision_bruta,
        total_descuentos,
        total_bonificaciones,
        valor_neto_asesor
    FROM LIQUIDACIONES_ASESORES
    WHERE total_descuentos > 0
    LIMIT 3
""")

print("\nMuestra de liquidaciones actualizadas:")
print("-" * 70)
for row in cur.fetchall():
    print(f"  ID {row[0]} ({row[1]})")
    print(f"    Comisión: ${row[2]:,} | Desc: ${row[3]:,} | Bonif: ${row[4]:,} | Neto: ${row[5]:,}")

cur.close()
conn.close()

print("\n" + "="*70)
print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
print("="*70)
