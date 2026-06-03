import sys
import os

# Añadir el directorio raíz al path para que las importaciones funcionen correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from migraciones.database_config import get_database_connection, DB_MODE

def sync_active_contracts():
    print(f"Modo de Base de Datos: {DB_MODE.upper()}")
    if DB_MODE != 'postgresql':
        print("Este script est\xe1 dise\xf1ado principalmente para la DB de producci\xf3n (PostgreSQL).")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Buscar todas las propiedades con Arrendamiento Activo y Mandato Activo
        query = """
        SELECT 
            p.ID_PROPIEDAD, 
            p.MATRICULA_INMOBILIARIA, 
            p.DIRECCION_PROPIEDAD,
            a.ID_CONTRATO_A,
            a.CANON_ARRENDAMIENTO,
            a.FECHA_INICIO_CONTRATO_A,
            a.FECHA_FIN_CONTRATO_A,
            a.DURACION_CONTRATO_A,
            m.ID_CONTRATO_M,
            m.CANON_MANDATO,
            m.FECHA_INICIO_CONTRATO_M,
            m.FECHA_FIN_CONTRATO_M,
            m.DURACION_CONTRATO_M,
            p.CANON_ARRENDAMIENTO_ESTIMADO,
            p.DISPONIBILIDAD_PROPIEDAD
        FROM PROPIEDADES p
        JOIN CONTRATOS_ARRENDAMIENTOS a ON p.ID_PROPIEDAD = a.ID_PROPIEDAD
        JOIN CONTRATOS_MANDATOS m ON p.ID_PROPIEDAD = m.ID_PROPIEDAD
        WHERE a.ESTADO_CONTRATO_A = 'ACTIVO' 
          AND m.ESTADO_CONTRATO_M = 'ACTIVO';
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Encontrados {len(rows)} pares de contratos activos (Arriendo + Mandato).")

        corregidos = 0
        for row in rows:
            (id_prop, matricula, direccion, id_a, canon_a, finicio_a, ffin_a, dur_a,
             id_m, canon_m, finicio_m, ffin_m, dur_m, canon_p, disp_p) = row

            necesita_sync = False
            updates_m = []
            params_m = []
            
            updates_p = []
            params_p = []

            # Validar y Sincronizar Canon
            if canon_a != canon_m:
                print(f"Propiedad {id_prop} ({direccion}): Discrepancia Canon Mandato (M: {canon_m} != A: {canon_a})")
                updates_m.append("CANON_MANDATO = %s")
                params_m.append(canon_a)
                necesita_sync = True

            if canon_a != canon_p:
                print(f"Propiedad {id_prop} ({direccion}): Discrepancia Canon Estimado Propiedad (P: {canon_p} != A: {canon_a})")
                updates_p.append("CANON_ARRENDAMIENTO_ESTIMADO = %s")
                params_p.append(canon_a)
                necesita_sync = True

            # Validar y Sincronizar Fechas
            if finicio_a != finicio_m or ffin_a != ffin_m or dur_a != dur_m:
                print(f"Propiedad {id_prop} ({direccion}): Discrepancia Fechas/Duraci\xf3n")
                updates_m.append("FECHA_INICIO_CONTRATO_M = %s")
                params_m.append(finicio_a)
                updates_m.append("FECHA_FIN_CONTRATO_M = %s")
                params_m.append(ffin_a)
                updates_m.append("DURACION_CONTRATO_M = %s")
                params_m.append(dur_a)
                
                # Calcular Grupo Operativo y d\xeda de pago
                # Convertimos finicio_a a string para extraer el d\xeda si es date, o usar datetime si es str
                from datetime import datetime
                if isinstance(finicio_a, str):
                    f_dt = datetime.strptime(finicio_a[:10], "%Y-%m-%d").date()
                else:
                    f_dt = finicio_a
                
                dia = f_dt.day
                if 1 <= dia <= 10:
                    grupo = 1
                    fpago = '10'
                elif 11 <= dia <= 20:
                    grupo = 2
                    fpago = '20'
                else:
                    grupo = 3
                    fpago = '-1'

                updates_m.append("GRUPO_OPERATIVO = %s")
                params_m.append(grupo)
                updates_m.append("FECHA_PAGO = %s")
                params_m.append(fpago)

                necesita_sync = True

            # Validar Disponibilidad Propiedad
            if disp_p is not False:
                print(f"Propiedad {id_prop} ({direccion}): Estado debe ser Ocupada (False) pero es {disp_p}")
                updates_p.append("DISPONIBILIDAD_PROPIEDAD = %s")
                params_p.append(False)
                necesita_sync = True

            # Aplicar actualizaciones
            if necesita_sync or id_prop == 38:
                # Forzar atenci\xf3n a la propiedad 38 si el usuario lo pidi\xf3, aunque se arregla con logic above
                if updates_m:
                    sql_m = f"UPDATE CONTRATOS_MANDATOS SET {', '.join(updates_m)}, UPDATED_AT = CURRENT_TIMESTAMP WHERE ID_CONTRATO_M = %s"
                    params_m.append(id_m)
                    cursor.execute(sql_m, tuple(params_m))
                
                if updates_p:
                    sql_p = f"UPDATE PROPIEDADES SET {', '.join(updates_p)}, UPDATED_AT = CURRENT_TIMESTAMP WHERE ID_PROPIEDAD = %s"
                    params_p.append(id_prop)
                    cursor.execute(sql_p, tuple(params_p))

                print(f"-> Sincronizaci\xf3n completada para Propiedad {id_prop}")
                corregidos += 1
            else:
                pass # print(f"Propiedad {id_prop} OK.")

        conn.commit()
        print(f"Terminado. {corregidos} propiedades/contratos corregidos y sincronizados de un total de {len(rows)}.")

    except Exception as e:
        conn.rollback()
        print(f"Error durante la sincronizaci\xf3n: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    sync_active_contracts()
