
import sqlite3

DB_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\DB_Inmo_Velar.db"

def fix_constraints():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Iniciando eliminación de constraints no determinísticos...")
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # 0. ELIMINAR VISTAS DEPENDIENTES
        print("Eliminando vistas dependientes...")
        cursor.execute("DROP VIEW IF EXISTS VW_ALERTA_MORA_DIARIA")
        cursor.execute("DROP VIEW IF EXISTS VW_ALERTA_VENCIMIENTO_CONTRATOS")
        cursor.execute("DROP VIEW IF EXISTS VW_REPORTE_DISPONIBLES")
        cursor.execute("DROP VIEW IF EXISTS VW_KPI_SIGNOS_VITALES") 
        cursor.execute("DROP VIEW IF EXISTS VW_AUDITORIA_FORENSE_PAGOS")
        cursor.execute("DROP VIEW IF EXISTS VW_KPI_YIELD_GAP")
        cursor.execute("DROP VIEW IF EXISTS VW_KPI_RIESGO_FLUJO_CAJA")

        
        # 1. CONTRATOS_MANDATOS
        print("Corrigiendo CONTRATOS_MANDATOS...")
        cursor.execute("ALTER TABLE CONTRATOS_MANDATOS RENAME TO CONTRATOS_MANDATOS_TEMP")
        
        # Nueva definición SIN el check de date('now')
        create_mandato = """
        CREATE TABLE CONTRATOS_MANDATOS (
            ID_CONTRATO_M INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_PROPIEDAD INTEGER NOT NULL,
            ID_PROPIETARIO INTEGER NOT NULL,
            ID_ASESOR INTEGER NOT NULL,
            FECHA_INICIO_CONTRATO_M TEXT NOT NULL,
            FECHA_FIN_CONTRATO_M TEXT NOT NULL,
            DURACION_CONTRATO_M INTEGER NOT NULL CHECK(DURACION_CONTRATO_M > 0),
            CANON_MANDATO INTEGER NOT NULL CHECK(CANON_MANDATO >= 500000 AND CANON_MANDATO <= 200000000),
            COMISION_PORCENTAJE_CONTRATO_M INTEGER NOT NULL CHECK(COMISION_PORCENTAJE_CONTRATO_M >= 0 AND COMISION_PORCENTAJE_CONTRATO_M <= 10000),
            IVA_CONTRATO_M INTEGER DEFAULT 1900 CHECK(IVA_CONTRATO_M >= 0),
            ESTADO_CONTRATO_M TEXT CHECK(ESTADO_CONTRATO_M IN ('Activo', 'Finalizado', 'Cancelado')) DEFAULT 'Activo',
            MOTIVO_CANCELACION TEXT,
            ALERTA_VENCIMINETO_CONTRATO_M INTEGER DEFAULT 1 CHECK(ALERTA_VENCIMINETO_CONTRATO_M IN (0, 1)),
            FECHA_RENOVACION_CONTRATO_M TEXT,
            CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            CREATED_BY TEXT,
            UPDATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            UPDATED_BY TEXT,
            CHECK(date(FECHA_FIN_CONTRATO_M) > date(FECHA_INICIO_CONTRATO_M)),
            FOREIGN KEY (ID_PROPIEDAD) REFERENCES PROPIEDADES(ID_PROPIEDAD),
            FOREIGN KEY (ID_PROPIETARIO) REFERENCES PROPIETARIOS(ID_PROPIETARIO),
            FOREIGN KEY (ID_ASESOR) REFERENCES ASESORES(ID_ASESOR)
        )
        """
        cursor.execute(create_mandato)
        cursor.execute("INSERT INTO CONTRATOS_MANDATOS SELECT * FROM CONTRATOS_MANDATOS_TEMP")
        cursor.execute("DROP TABLE CONTRATOS_MANDATOS_TEMP")
        cursor.execute("CREATE UNIQUE INDEX idx_mandato_activo ON CONTRATOS_MANDATOS(ID_PROPIEDAD) WHERE ESTADO_CONTRATO_M = 'Activo'")

        # 2. CONTRATOS_ARRENDAMIENTOS
        print("Corrigiendo CONTRATOS_ARRENDAMIENTOS...")
        cursor.execute("ALTER TABLE CONTRATOS_ARRENDAMIENTOS RENAME TO CONTRATOS_ARRENDAMIENTOS_TEMP")
        
        # Nueva definición SIN el check de date('now')
        create_arriendo = """
        CREATE TABLE CONTRATOS_ARRENDAMIENTOS (
            ID_CONTRATO_A INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_PROPIEDAD INTEGER NOT NULL,
            ID_ARRENDATARIO INTEGER NOT NULL,
            ID_CODEUDOR INTEGER,
            FECHA_INICIO_CONTRATO_A TEXT NOT NULL,
            FECHA_FIN_CONTRATO_A TEXT NOT NULL,
            DURACION_CONTRATO_A INTEGER NOT NULL CHECK(DURACION_CONTRATO_A > 0),
            CANON_ARRENDAMIENTO INTEGER NOT NULL CHECK(CANON_ARRENDAMIENTO >= 500000 AND CANON_ARRENDAMIENTO <= 200000000),
            DEPOSITO INTEGER DEFAULT 0 CHECK(DEPOSITO >= 0),
            ESTADO_CONTRATO_A TEXT CHECK(ESTADO_CONTRATO_A IN ('Activo', 'Finalizado', 'Legal', 'Cancelado')) DEFAULT 'Activo',
            MOTIVO_CANCELACION TEXT,
            ALERTA_VENCIMIENTO_CONTRATO_A INTEGER DEFAULT 1 CHECK(ALERTA_VENCIMIENTO_CONTRATO_A IN (0, 1)),
            ALERTA_IPC INTEGER DEFAULT 0 CHECK(ALERTA_IPC IN (0, 1)),
            FECHA_RENOVACION_CONTRATO_A TEXT,
            FECHA_INCREMENTO_IPC TEXT,
            FECHA_ULTIMO_INCREMENTO_IPC TEXT,
            CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            CREATED_BY TEXT,
            UPDATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            UPDATED_BY TEXT,
            CHECK(date(FECHA_FIN_CONTRATO_A) > date(FECHA_INICIO_CONTRATO_A)),
            FOREIGN KEY (ID_PROPIEDAD) REFERENCES PROPIEDADES(ID_PROPIEDAD),
            FOREIGN KEY (ID_ARRENDATARIO) REFERENCES ARRENDATARIOS(ID_ARRENDATARIO),
            FOREIGN KEY (ID_CODEUDOR) REFERENCES CODEUDORES(ID_CODEUDOR)
        )
        """
        cursor.execute(create_arriendo)
        cursor.execute("INSERT INTO CONTRATOS_ARRENDAMIENTOS SELECT * FROM CONTRATOS_ARRENDAMIENTOS_TEMP")
        cursor.execute("DROP TABLE CONTRATOS_ARRENDAMIENTOS_TEMP")
        cursor.execute("CREATE UNIQUE INDEX idx_arriendo_activo ON CONTRATOS_ARRENDAMIENTOS(ID_PROPIEDAD) WHERE ESTADO_CONTRATO_A = 'Activo'")

        conn.commit()
        print("Corrección exitosa.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error durante corrección: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_constraints()
