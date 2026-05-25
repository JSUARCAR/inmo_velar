import sys
import os
import csv
import subprocess

# Añadir el root al path para importar
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from migraciones.database_config import get_database_connection, get_database_url

def run_audit():
    try:
        conn = get_database_connection()
        import psycopg2.extras
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        md_output = "# Auditoría Fase 0 - Disponibilidad\n\n"
        
        # 6.1
        q6_1 = """
        SELECT
            p.ID_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            p.DIRECCION_PROPIEDAD,
            p.DISPONIBILIDAD_PROPIEDAD,
            'OCUPADA_SIN_CONTRATO' as TIPO_INCONSISTENCIA
        FROM PROPIEDADES p
        WHERE p.DISPONIBILIDAD_PROPIEDAD = FALSE
          AND p.ESTADO_REGISTRO = TRUE
          AND NOT EXISTS (
              SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
              WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                AND ca.ESTADO_CONTRATO_A = 'Activo'
          );
        """
        cursor.execute(q6_1)
        res_6_1 = cursor.fetchall()
        md_output += f"## 6.1 Propiedades OCUPADAS sin contrato ACTIVO\nEncontradas: {len(res_6_1)}\n"
        
        # 6.2
        q6_2 = """
        SELECT
            p.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD,
            ca.ID_CONTRATO_A,
            ca.ESTADO_CONTRATO_A,
            p.DISPONIBILIDAD_PROPIEDAD,
            'DISPONIBLE_CON_CONTRATO' as TIPO_INCONSISTENCIA
        FROM PROPIEDADES p
        INNER JOIN CONTRATOS_ARRENDAMIENTOS ca
            ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
        WHERE p.DISPONIBILIDAD_PROPIEDAD = TRUE
          AND ca.ESTADO_CONTRATO_A = 'Activo';
        """
        cursor.execute(q6_2)
        res_6_2 = cursor.fetchall()
        md_output += f"## 6.2 Propiedades DISPONIBLES con contrato ACTIVO\nEncontradas: {len(res_6_2)}\n"
        
        # 6.3
        q6_3 = """
        SELECT
            ca.ID_CONTRATO_A,
            ca.ESTADO_CONTRATO_A,
            ca.FECHA_FIN_CONTRATO_A,
            p.ID_PROPIEDAD,
            p.DISPONIBILIDAD_PROPIEDAD,
            'TERMINADO_SIN_LIBERAR' as TIPO_INCONSISTENCIA
        FROM CONTRATOS_ARRENDAMIENTOS ca
        INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        WHERE ca.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado')
          AND p.DISPONIBILIDAD_PROPIEDAD = FALSE;
        """
        cursor.execute(q6_3)
        res_6_3 = cursor.fetchall()
        md_output += f"## 6.3 Contratos FINALIZADOS/CANCELADOS con propiedad OCUPADA\nEncontradas: {len(res_6_3)}\n"
        
        # 6.4
        q6_4 = """
        SELECT
            ca.ID_CONTRATO_A,
            ca.ESTADO_CONTRATO_A,
            ca.FECHA_INICIO_CONTRATO_A,
            p.ID_PROPIEDAD,
            p.DISPONIBILIDAD_PROPIEDAD,
            'ACTIVO_SIN_OCUPAR' as TIPO_INCONSISTENCIA
        FROM CONTRATOS_ARRENDAMIENTOS ca
        INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
          AND p.DISPONIBILIDAD_PROPIEDAD = TRUE;
        """
        cursor.execute(q6_4)
        res_6_4 = cursor.fetchall()
        md_output += f"## 6.4 Contratos ACTIVOS sin propiedad OCUPADA\nEncontradas: {len(res_6_4)}\n"
        
        # 6.5
        q6_5 = """
        SELECT
            ca.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD,
            COUNT(*) as CONTRATOS_ACTIVOS,
            STRING_AGG(ca.ID_CONTRATO_A::TEXT, ', ') as IDS_CONTRATOS
        FROM CONTRATOS_ARRENDAMIENTOS ca
        INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
        GROUP BY ca.ID_PROPIEDAD, p.DIRECCION_PROPIEDAD
        HAVING COUNT(*) > 1;
        """
        cursor.execute(q6_5)
        res_6_5 = cursor.fetchall()
        md_output += f"## 6.5 Propiedades con múltiples contratos ACTIVOS\nEncontradas: {len(res_6_5)}\n"
        
        # 6.6
        q6_6 = """
        WITH
        ocupadas_sin_contrato AS (
            SELECT p.ID_PROPIEDAD FROM PROPIEDADES p
            WHERE p.DISPONIBILIDAD_PROPIEDAD = FALSE
              AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD AND ca.ESTADO_CONTRATO_A = 'Activo')
        ),
        disponibles_con_contrato AS (
            SELECT p.ID_PROPIEDAD FROM PROPIEDADES p
            JOIN CONTRATOS_ARRENDAMIENTOS ca ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
            WHERE p.DISPONIBILIDAD_PROPIEDAD = TRUE AND ca.ESTADO_CONTRATO_A = 'Activo'
        ),
        terminados_ocupados AS (
            SELECT p.ID_PROPIEDAD FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            WHERE ca.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado') AND p.DISPONIBILIDAD_PROPIEDAD = FALSE
        ),
        multiples_activos AS (
            SELECT ca.ID_PROPIEDAD FROM CONTRATOS_ARRENDAMIENTOS ca
            WHERE ca.ESTADO_CONTRATO_A = 'Activo'
            GROUP BY ca.ID_PROPIEDAD HAVING COUNT(*) > 1
        )
        SELECT
            'OCUPADA_SIN_CONTRATO' as INCONSISTENCIA, COUNT(*) as TOTAL FROM ocupadas_sin_contrato
        UNION ALL
        SELECT 'DISPONIBLE_CON_CONTRATO', COUNT(*) FROM disponibles_con_contrato
        UNION ALL
        SELECT 'TERMINADO_SIN_LIBERAR', COUNT(*) FROM terminados_ocupados
        UNION ALL
        SELECT 'MULTIPLES_ACTIVOS', COUNT(*) FROM multiples_activos;
        """
        cursor.execute(q6_6)
        res_6_6 = cursor.fetchall()
        md_output += f"## 6.6 Resumen consolidado\n"
        for r in res_6_6:
            md_output += f"- {r['inconsistencia']}: {r['total']}\n"
        
        # Triggers
        q_triggers = """
        SELECT trigger_name, event_manipulation, event_object_table, action_statement
        FROM information_schema.triggers
        WHERE event_object_table IN ('contratos_arrendamientos', 'propiedades')
        ORDER BY event_object_table, trigger_name;
        """
        cursor.execute(q_triggers)
        res_triggers = cursor.fetchall()
        md_output += f"\n## Triggers existentes en BD\n"
        for r in res_triggers:
            md_output += f"- `{r['event_object_table']}`: `{r['trigger_name']}` ({r['event_manipulation']})\n"
            
        with open('scripts/diagnostico/audit_fase_0_disponibilidad_report.md', 'w', encoding='utf-8') as f:
            f.write(md_output)
            
        print("Auditoría generada en scripts/diagnostico/audit_fase_0_disponibilidad_report.md")
        
        # Export properties to CSV
        cursor.execute("SELECT * FROM PROPIEDADES")
        props = cursor.fetchall()
        with open('scripts/diagnostico/snapshot_propiedades.csv', 'w', newline='', encoding='utf-8') as csvf:
            if props:
                writer = csv.writer(csvf)
                writer.writerow(props[0].keys())
                for r in props:
                    writer.writerow(r.values())
        print("Snapshot de propiedades exportado.")
        
        cursor.execute("SELECT * FROM CONTRATOS_ARRENDAMIENTOS")
        contratos = cursor.fetchall()
        with open('scripts/diagnostico/snapshot_contratos.csv', 'w', newline='', encoding='utf-8') as csvf:
            if contratos:
                writer = csv.writer(csvf)
                writer.writerow(contratos[0].keys())
                for r in contratos:
                    writer.writerow(r.values())
        print("Snapshot de contratos exportado.")
        
        # Backup BD
        print("Iniciando pg_dump...")
        db_url = get_database_url()
        if not db_url:
            print("No se encontró DATABASE_URL, omitiendo pg_dump")
        else:
            try:
                subprocess.run(['pg_dump', db_url, '-f', 'scripts/diagnostico/backup_db_fase_0.sql', '--clean', '--if-exists'], check=True, timeout=120)
                print("Backup pg_dump exitoso.")
            except Exception as e:
                print(f"No se pudo ejecutar pg_dump o falló: {e}")
                
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_audit()
