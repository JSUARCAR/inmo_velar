import sys
import os
# Asegurar que el path incluya la raiz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection

def eliminar_duplicados():
    query_verificacion = """
        SELECT count(*) FROM (
            SELECT ROW_NUMBER() OVER (
                PARTITION BY id_contrato_a, fecha_pago, valor_total
                ORDER BY id_recaudo ASC
            ) as row_num
            FROM recaudos
            WHERE fecha_pago = '2026-04-03'
        ) t WHERE row_num > 1;
    """

    query_eliminacion = """
        WITH duplicados AS (
            SELECT
                id_recaudo,
                ROW_NUMBER() OVER (
                    PARTITION BY id_contrato_a, fecha_pago, valor_total
                    ORDER BY id_recaudo ASC
                ) as row_num
            FROM recaudos
            WHERE fecha_pago = '2026-04-03'
        )
        DELETE FROM recaudos
        WHERE id_recaudo IN (
            SELECT id_recaudo
            FROM duplicados
            WHERE row_num > 1
        )
        RETURNING id_recaudo;
    """

    conn = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        # 1. Verificar cuantos se borraran
        cursor.execute(query_verificacion)
        result = cursor.fetchone()
        cantidad_duplicados = result[0] if result else 0

        if cantidad_duplicados == 0:
            print("No se encontraron recaudos duplicados para la fecha 2026-04-03.")
            return

        print(f"Se detectaron {cantidad_duplicados} registros duplicados. Procediendo a eliminar...")

        # 2. Ejecutar borrado
        cursor.execute(query_eliminacion)
        deleted_rows = cursor.fetchall()

        conn.commit()
        print(f"Exito: Se eliminaron {len(deleted_rows)} registros duplicados correctamente en Railway.")
        for row in deleted_rows:
            print(f" - ID eliminado: {row[0]}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error critico durante la ejecucion (Transaccion Revertida): {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    eliminar_duplicados()
