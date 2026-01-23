
import sqlite3

DB_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\DB_Inmo_Velar.db"

def restore_objects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Iniciando restauración de Triggers y Vistas...")
    
    try:
        cursor.execute("BEGIN TRANSACTION")

        # ==========================================
        # TRIGGERS
        # ==========================================
        print("Restaurando Triggers...")

        triggers = [
            """
            CREATE TRIGGER IF NOT EXISTS TRG_AUDITORIA_CONTRATOS_A_UPDATE
            AFTER UPDATE ON CONTRATOS_ARRENDAMIENTOS
            BEGIN
                INSERT INTO AUDITORIA_CAMBIOS (TABLA, ID_REGISTRO, TIPO_OPERACION, CAMPO_MODIFICADO, VALOR_ANTERIOR, VALOR_NUEVO, USUARIO, MOTIVO_CAMBIO)
                SELECT 'CONTRATOS_ARRENDAMIENTOS', OLD.ID_CONTRATO_A, 'UPDATE', 'ESTADO_CONTRATO_A', OLD.ESTADO_CONTRATO_A, NEW.ESTADO_CONTRATO_A, 'SISTEMA', NEW.MOTIVO_CANCELACION
                WHERE OLD.ESTADO_CONTRATO_A <> NEW.ESTADO_CONTRATO_A;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_PREVENIR_DELETE_CONTRATOS
            BEFORE DELETE ON CONTRATOS_ARRENDAMIENTOS
            BEGIN
                SELECT RAISE(ABORT, 'Error: No está permitido eliminar contratos físicamente. Debe cambiar su estado a "Cancelado" o "Finalizado" para mantener el histórico.');
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_VALIDAR_FECHAS_CONTRATO
            BEFORE INSERT ON CONTRATOS_ARRENDAMIENTOS
            BEGIN
                SELECT RAISE(ABORT, 'Error: La fecha de finalización no puede ser anterior a la fecha de inicio.')
                WHERE NEW.FECHA_FIN_CONTRATO_A <= NEW.FECHA_INICIO_CONTRATO_A;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_EVITAR_SOLAPAMIENTO_ARRIENDO
            BEFORE INSERT ON CONTRATOS_ARRENDAMIENTOS
            BEGIN
                SELECT RAISE(ABORT, 'Error: Esta propiedad ya tiene un contrato de arrendamiento ACTIVO. Debe finalizar el anterior primero.')
                WHERE EXISTS (
                    SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS 
                    WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD 
                    AND ESTADO_CONTRATO_A = 'Activo'
                );
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_EVITAR_SOLAPAMIENTO_MANDATO
            BEFORE INSERT ON CONTRATOS_MANDATOS
            BEGIN
                SELECT RAISE(ABORT, 'Error: Esta propiedad ya tiene un contrato de mandato ACTIVO.')
                WHERE EXISTS (
                    SELECT 1 FROM CONTRATOS_MANDATOS 
                    WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD 
                    AND ESTADO_CONTRATO_M = 'Activo'
                );
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA
            AFTER INSERT ON CONTRATOS_ARRENDAMIENTOS
            WHEN NEW.ESTADO_CONTRATO_A = 'Activo'
            BEGIN
                UPDATE PROPIEDADES 
                SET DISPONIBILIDAD_PROPIEDAD = 0 
                WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE
            AFTER UPDATE ON CONTRATOS_ARRENDAMIENTOS
            WHEN NEW.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado') 
            AND OLD.ESTADO_CONTRATO_A = 'Activo'
            BEGIN
                UPDATE PROPIEDADES 
                SET DISPONIBILIDAD_PROPIEDAD = 1 
                WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
            END;
            """,
            """
            CREATE TRIGGER IF NOT EXISTS TRG_EXIGIR_MOTIVO_CANCELACION
            BEFORE UPDATE ON CONTRATOS_ARRENDAMIENTOS
            WHEN NEW.ESTADO_CONTRATO_A = 'Cancelado' 
            AND (NEW.MOTIVO_CANCELACION IS NULL OR NEW.MOTIVO_CANCELACION = '')
            BEGIN
                SELECT RAISE(ABORT, 'Error: Para cancelar un contrato es OBLIGATORIO ingresar un motivo de cancelación.');
            END;
            """
        ]

        for trigger in triggers:
            cursor.execute(trigger)

        # ==========================================
        # VISTAS
        # ==========================================
        print("Restaurando Vistas...")

        views = [
            """
            DROP VIEW IF EXISTS VW_ALERTA_MORA_DIARIA;
            """,
            """
            CREATE VIEW VW_ALERTA_MORA_DIARIA AS
            SELECT 
                r.ID_RECAUDO,
                ca.ID_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                arr_p.NOMBRE_COMPLETO AS ARRENDATARIO,
                arr_p.TELEFONO_PRINCIPAL,
                r.VALOR_RECAUDO,
                r.FECHA_VENCIMIENTO_RECAUDO,
                date('now') AS FECHA_HOY,
                CAST((julianday('now') - julianday(r.FECHA_VENCIMIENTO_RECAUDO)) AS INTEGER) AS DIAS_RETRASO
            FROM RECAUDO_ARRENDAMIENTO r
            JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
            WHERE r.ESTADO_RECAUDO IN ('Pendiente', 'Mora')
            AND r.FECHA_VENCIMIENTO_RECAUDO < date('now');
            """,
            """
            DROP VIEW IF EXISTS VW_ALERTA_VENCIMIENTO_CONTRATOS;
            """,
            """
            CREATE VIEW VW_ALERTA_VENCIMIENTO_CONTRATOS AS
            SELECT 
                ca.ID_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                arr_p.NOMBRE_COMPLETO AS ARRENDATARIO,
                arr_p.TELEFONO_PRINCIPAL, 
                ca.FECHA_FIN_CONTRATO_A,
                CAST((julianday(ca.FECHA_FIN_CONTRATO_A) - julianday('now')) AS INTEGER) AS DIAS_RESTANTES
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
            WHERE ca.ESTADO_CONTRATO_A = 'Activo'
            AND ca.FECHA_FIN_CONTRATO_A <= date('now', '+90 days');
            """,
            """
            DROP VIEW IF EXISTS VW_REPORTE_DISPONIBLES;
            """,
            """
            CREATE VIEW VW_REPORTE_DISPONIBLES AS
            SELECT 
                p.ID_PROPIEDAD,
                m.NOMBRE_MUNICIPIO AS CIUDAD,
                p.DIRECCION_PROPIEDAD,
                p.ESTRATO,
                p.CANON_ARRENDAMIENTO_ESTIMADO AS CANON,
                p.AREA_M2,
                p.HABITACIONES,
                p.BANO
            FROM PROPIEDADES p
            JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
            WHERE p.DISPONIBILIDAD_PROPIEDAD = 1
            AND p.ESTADO_REGISTRO = 1;
            """
        ]

        for view in views:
            cursor.execute(view)

        conn.commit()
        print("Restauración exitosa.")

    except Exception as e:
        conn.rollback()
        print(f"Error durante restauración: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    restore_objects()
