"""
Script de Migracion: Agregar estado VENCIDO a tabla RECAUDOS

Agrega el nuevo estado 'Vencido' al CHECK constraint de ESTADO_RECAUDO
para permitir que los recaudos generados masivamente puedan marcarse
como vencidos cuando la fecha de pago calculada es anterior a la fecha actual.

Este cambio supporta la funcionalidad de:
- Fecha de pago basada en el dia de inicio del contrato de arrendamiento
- Estado automatico Vencido/Pendiente segun corresponda

Compatible con SQLite (desarrollo) y PostgreSQL (produccion).
"""

import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ejecutar_migracion():
    """Ejecuta la migracion para agregar estado Vencido a RECAUDOS."""

    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DB_Inmo_Velar.db"
    )

    print("=" * 60)
    print("MIGRACION: Agregar estado 'Vencido' a RECAUDOS")
    print("=" * 60)
    print(f"\nBase de datos: {db_path}")

    if not os.path.exists(db_path):
        print(f"[ERROR] No se encontro la base de datos en {db_path}")
        print(
            "Nota: Si usa PostgreSQL, ejecute el SQL directamente en la base de datos."
        )
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n1. Verificando estado actual de la tabla RECAUDOS...")
        cursor.execute("PRAGMA table_info(RECAUDOS)")
        columnas = {row[1] for row in cursor.fetchall()}
        print(f"   Columnas existentes: {len(columnas)}")

        if not columnas:
            print("\n   La tabla RECAUDOS no existe. Verificando tablas existentes...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = cursor.fetchall()
            print(f"   Tablas: {[t[0] for t in tablas]}")
            print(
                "\n   Nota: Esta base de datos SQLite local no tiene la tabla RECAUDOS."
            )
            print(
                "   La tabla probablemente esta en PostgreSQL. Ejecute el SQL manualmente:"
            )
            print(
                "   ALTER TABLE RECAUDOS DROP CONSTRAINT IF EXISTS estado_recaudo_check;"
            )
            print("   ALTER TABLE RECAUDOS ADD CONSTRAINT estado_recaudo_check")
            print(
                "   CHECK (ESTADO_RECAUDO IN ('Pendiente', 'Aplicado', 'Reversado', 'Vencido'));"
            )
            conn.close()
            return True

        print("\n2. Verificando constraint actual...")
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='RECAUDOS'
        """)
        table_result = cursor.fetchone()
        if not table_result:
            print("[ERROR] No se pudo obtener el schema de la tabla")
            return False

        table_sql = table_result[0]
        print(f"   CREATE TABLE actual (primeros 200 chars):")
        print(f"   {table_sql[:200]}...")

        print("\n3. Verificando valores actuales en ESTADO_RECAUDO...")
        cursor.execute("SELECT DISTINCT ESTADO_RECAUDO FROM RECAUDOS")
        estados = cursor.fetchall()
        print(f"   Estados actuales: {[e[0] for e in estados]}")

        print("\n4. Eliminando constraint antiguo y creando nuevo...")
        cursor.execute("PRAGMA foreign_keys = OFF")

        cursor.execute("""
            ALTER TABLE RECAUDOS 
            DROP COLUMN IF EXISTS fake_column
        """)
        conn.commit()

        print("\n5. Recreando tabla con nuevo constraint...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS RECAUDOS_NUEVO (
                ID_RECAUDO INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_CONTRATO_A INTEGER NOT NULL,
                FECHA_PAGO TEXT NOT NULL,
                VALOR_TOTAL INTEGER NOT NULL CHECK(VALOR_TOTAL > 0),
                METODO_PAGO TEXT NOT NULL CHECK(METODO_PAGO IN ('Efectivo', 'Transferencia', 'PSE', 'Consignacion')),
                REFERENCIA_BANCARIA TEXT,
                ESTADO_RECAUDO TEXT DEFAULT 'Pendiente' CHECK(ESTADO_RECAUDO IN ('Pendiente', 'Aplicado', 'Reversado', 'Vencido')),
                OBSERVACIONES TEXT,
                CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A)
            )
        """)

        cursor.execute("""
            INSERT INTO RECAUDOS_NUEVO (
                ID_RECAUDO, ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL,
                METODO_PAGO, REFERENCIA_BANCARIA, ESTADO_RECAUDO,
                OBSERVACIONES, CREATED_AT, CREATED_BY, UPDATED_AT, UPDATED_BY
            )
            SELECT 
                ID_RECAUDO, ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL,
                METODO_PAGO, REFERENCIA_BANCARIA, ESTADO_RECAUDO,
                OBSERVACIONES, CREATED_AT, CREATED_BY, UPDATED_AT, UPDATED_BY
            FROM RECAUDOS
        """)

        cursor.execute("DROP TABLE IF EXISTS RECAUDOS")
        cursor.execute("ALTER TABLE RECAUDOS_NUEVO RENAME TO RECAUDOS")

        cursor.execute("PRAGMA foreign_keys = ON")
        conn.commit()

        print("\n6. Verificando migracion...")
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='RECAUDOS'
        """)
        nueva_tabla = cursor.fetchone()[0]
        assert "Vencido" in nueva_tabla, "[ERROR] El constraint no incluye Vencido"

        print("   [OK] Constraint verificado correctamente")

        print("\n7. Verificando datos migrados...")
        cursor.execute("SELECT COUNT(*) FROM RECAUDOS")
        count = cursor.fetchone()[0]
        print(f"   Total registros: {count}")

        cursor.execute("SELECT DISTINCT ESTADO_RECAUDO FROM RECAUDOS")
        estados_nuevos = cursor.fetchall()
        print(f"   Estados disponibles: {[e[0] for e in estados_nuevos]}")

        conn.close()

        print("\n" + "=" * 60)
        print("[OK] MIGRACION COMPLETADA")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] en migracion: {str(e)}")
        if "conn" in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    resultado = ejecutar_migracion()
    sys.exit(0 if resultado else 1)
