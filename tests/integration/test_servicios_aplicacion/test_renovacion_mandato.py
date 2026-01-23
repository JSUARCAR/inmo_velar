
import sys
import os
import sqlite3
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.configuracion.settings import obtener_configuracion
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.entidades.contrato_mandato import ContratoMandato

def verify_renovacion_mandato():
    try:
        config = obtener_configuracion()
        print(f"DB: {config.database_path}")
        db = DatabaseManager()
        servicio = ServicioContratos(db)
        
        # 1. SETUP: Borrar datos de prueba anteriores
        with db.obtener_conexion() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM RENOVACIONES_CONTRATOS")
            c.execute("DELETE FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD=99999")
            # Create needed entities stub
            c.execute("INSERT OR IGNORE INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) VALUES (99999, 'MUNI TEST M', 'DEP TEST M', 1)")
            c.execute("INSERT OR IGNORE INTO PROPIEDADES (ID_PROPIEDAD, MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO, ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO, CANON_ARRENDAMIENTO_ESTIMADO) VALUES (99999, 'TEST-MANDATO', 'Calle Mandato Test', 1, 99999, 'Casa', 100, 4, 2000000)")
            c.execute("INSERT OR IGNORE INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES ('PROPIETARIO-TEST', 'Propietario Test')")
            conn.commit()
            c.execute("SELECT ID_PERSONA FROM PERSONAS WHERE NUMERO_DOCUMENTO='PROPIETARIO-TEST'")
            id_persona = c.fetchone()[0]
            c.execute("INSERT OR IGNORE INTO PROPIETARIOS (ID_PERSONA, ID_PROPIETARIO) VALUES (?, 99999)", (id_persona,))
            conn.commit()

            c.execute("INSERT OR IGNORE INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES ('ASESOR-TEST', 'Asesor Test')")
            conn.commit()
            c.execute("SELECT ID_PERSONA FROM PERSONAS WHERE NUMERO_DOCUMENTO='ASESOR-TEST'")
            id_persona_asesor = c.fetchone()[0]
            c.execute("INSERT OR IGNORE INTO ASESORES (ID_PERSONA, COMISION_PORCENTAJE_ARRIENDO, COMISION_PORCENTAJE_VENTA) VALUES (?, 800, 300)", (id_persona_asesor,))
            conn.commit()
            c.execute("SELECT ID_ASESOR FROM ASESORES WHERE ID_PERSONA=?", (id_persona_asesor,))
            id_asesor = c.fetchone()[0]

        # 2. CREAR CONTRATO MANDATO
        print("Creando contrato mandato...")
        fecha_fin_original = "2025-06-30"
        canon_original = 2000000
        
        contrato = ContratoMandato(
            id_contrato_m=None,
            id_propiedad=99999,
            id_propietario=99999,
            id_asesor=id_asesor, 
            fecha_inicio_contrato_m="2024-06-30",
            fecha_fin_contrato_m=fecha_fin_original,
            duracion_contrato_m=12,
            canon_mandato=canon_original,
            comision_porcentaje_contrato_m=10,
            iva_contrato_m=19,
            estado_contrato_m='Activo',
            alerta_vencimiento_contrato_m=1
        )
        
        # Usamos repo directo ya que servicio.crear_mandato no fue modificado en este task
        # Pero mejor usamos servicio.repo_mandato
        nuevo_contrato = servicio.repo_mandato.crear(contrato, "test_script")
        print(f"Mandato Creado: ID {nuevo_contrato.id_contrato_m}, Fin: {nuevo_contrato.fecha_fin_contrato_m}, Canon: {nuevo_contrato.canon_mandato}")

        # 3. RENOVAR
        print("Ejecutando servicio.renovar_mandato...")
        servicio.renovar_mandato(nuevo_contrato.id_contrato_m, "test_script")
        
        # 4. VERIFICAR
        mandato_renovado = servicio.repo_mandato.obtener_por_id(nuevo_contrato.id_contrato_m)
        print(f"Mandato Renovado: ID {mandato_renovado.id_contrato_m}, Fin: {mandato_renovado.fecha_fin_contrato_m}, Canon: {mandato_renovado.canon_mandato}")
        
        # Checks
        if mandato_renovado.canon_mandato == canon_original:
            print(">>> SUCCESS: El canon se mantuvo IGUAL (Correcto).")
        else:
            print(f">>> FAILURE: El canon cambió a {mandato_renovado.canon_mandato} (Incorrecto).")
            
        if mandato_renovado.fecha_fin_contrato_m > fecha_fin_original:
             print(f">>> SUCCESS: La fecha fin se extendió a {mandato_renovado.fecha_fin_contrato_m} (Correcto).")
        else:
             print(f">>> FAILURE: La fecha fin NO se extendió.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_renovacion_mandato()
