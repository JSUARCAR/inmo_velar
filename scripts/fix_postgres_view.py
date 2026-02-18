import os
import sys

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def fix_postgres_view():
    print("=== Corrigiendo Vista VW_ALERTA_VENCIMIENTO_CONTRATOS en PostgreSQL ===")
    
    if not db_manager.use_postgresql:
        print("[ERROR] Este script debe ejecutarse con una conexión a PostgreSQL configurada.")
        return False

    try:
        # SQL para crear la vista compatible con PostgreSQL
        # Incluye ambos tipos de contratos y usa sintaxis de fechas de PG
        sql_view = """
        CREATE OR REPLACE VIEW VW_ALERTA_VENCIMIENTO_CONTRATOS AS
            -- Contratos de Arrendamiento
            SELECT 
                'Arrendamiento' AS TIPO_CONTRATO,
                ca."id_contrato_a" AS ID_CONTRATO,
                ca."id_propiedad",
                p."direccion_propiedad" AS DIRECCION,
                per."nombre_completo" AS INQUILINO_PROPIETARIO,
                ca."fecha_fin_contrato_a" AS FECHA_FIN,
                (ca."fecha_fin_contrato_a"::DATE - CURRENT_DATE) AS DIAS_RESTANTES
            FROM "contratos_arrendamientos" ca
            JOIN "propiedades" p ON ca."id_propiedad" = p."id_propiedad"
            JOIN "arrendatarios" arr ON ca."id_arrendatario" = arr."id_arrendatario"
            JOIN "personas" per ON arr."id_persona" = per."id_persona"
            WHERE ca."estado_contrato_a" = 'Activo'
            AND ca."fecha_fin_contrato_a"::DATE <= (CURRENT_DATE + INTERVAL '90 days')
            
            UNION ALL
            
            -- Contratos de Mandato
            SELECT 
                'Mandato' AS TIPO_CONTRATO,
                cm."id_contrato_m" AS ID_CONTRATO,
                cm."id_propiedad",
                p."direccion_propiedad" AS DIRECCION,
                per."nombre_completo" AS INQUILINO_PROPIETARIO,
                cm."fecha_fin_contrato_m" AS FECHA_FIN,
                (cm."fecha_fin_contrato_m"::DATE - CURRENT_DATE) AS DIAS_RESTANTES
            FROM "contratos_mandatos" cm
            JOIN "propiedades" p ON cm."id_propiedad" = p."id_propiedad"
            JOIN "propietarios" prop ON cm."id_propietario" = prop."id_propietario"
            JOIN "personas" per ON prop."id_persona" = per."id_persona"
            WHERE cm."estado_contrato_m" = 'Activo'
            AND cm."fecha_fin_contrato_m"::DATE <= (CURRENT_DATE + INTERVAL '90 days')
            
            ORDER BY DIAS_RESTANTES ASC;
        """
        
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # 1. Eliminar vista existente si la hay
            print("[INFO] Eliminando vista anterior...")
            cursor.execute("DROP VIEW IF EXISTS VW_ALERTA_VENCIMIENTO_CONTRATOS CASCADE;")
            
            # 2. Crear nueva vista
            print("[INFO] Creando nueva vista optimizada para PostgreSQL...")
            cursor.execute(sql_view)
            
            conn.commit()
            print("[OK] Vista creada exitosamente.")
            
            # 3. Verificación
            print("\n=== Verificando contenido ===")
            cursor.execute('SELECT * FROM VW_ALERTA_VENCIMIENTO_CONTRATOS')
            rows = cursor.fetchall()
            print(f"Total registros encontrados: {len(rows)}")
            
            for row in rows:
                # El cursor retorna diccionario o tupla dependiendo del wrapper, 
                # pero db_manager suele devolver dicts en mayusculas o minúsculas según config.
                # Asumimos acceso por key o índice para mostrar info básica.
                print(f" - {row}")

    except Exception as e:
        print(f"[ERROR] Falló la actualización de la vista: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    fix_postgres_view()
