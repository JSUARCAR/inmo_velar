
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade

def get_datos_contrato_mandato(contrato_id: int) -> Dict[str, Any]:
    db = DatabaseManager()
    repo = RepositorioContratoMandatoSQLite(db)
    contrato = repo.obtener_por_id(contrato_id)
    
    if not contrato:
        raise ValueError(f"Contrato {contrato_id} no encontrado")
        
    # Obtener detalles completos
    with db.obtener_conexion() as conn:
        cursor = db.get_dict_cursor(conn)
        placeholder = db.get_placeholder()
        
        # Propietario
        cursor.execute(f"SELECT p.*, per.* FROM PROPIETARIOS p JOIN PERSONAS per ON p.ID_PERSONA = per.ID_PERSONA WHERE p.ID_PROPIETARIO = {placeholder}", (contrato.id_propietario,))
        prop = cursor.fetchone()
        
        # Propiedad
        cursor.execute(f"SELECT * FROM PROPIEDADES WHERE ID_PROPIEDAD = {placeholder}", (contrato.id_propiedad,))
        inmueble = cursor.fetchone()
        
    datos = {
        "contrato_id": contrato.id_contrato_m,
        "tipo_contrato": "MANDATO",
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "fecha_inicio": contrato.fecha_inicio_contrato_m,
        "fecha_fin": contrato.fecha_fin_contrato_m,
        "estado": "oficial",
        "mandante": {
            "nombre": prop["NOMBRE_COMPLETO"] if prop else "N/A",
            "documento": prop["NUMERO_DOCUMENTO"] if prop else "N/A",
            "telefono": prop["TELEFONO_PRINCIPAL"] if prop else "N/A",
            "email": prop["CORREO_ELECTRONICO"] if prop else "N/A",
            "banco": prop["BANCO_PROPIETARIO"] if prop else "N/A",
            "tipo_cuenta": prop["TIPO_CUENTA"] if prop else "N/A",
            "numero_cuenta": prop["NUMERO_CUENTA_PROPIETARIO"] if prop else "N/A",
        },
        "inmueble": {
            "direccion": inmueble["DIRECCION_PROPIEDAD"] if inmueble else "N/A",
            "matricula_inmobiliaria": inmueble["MATRICULA_INMOBILIARIA"] if inmueble else "N/A",
            "municipio": "ARMENIA", # Simplificado
            "departamento": "QUINDÍO", # Simplificado
            "tipo": inmueble["TIPO_PROPIEDAD"] if inmueble else "N/A",
        },
        "condiciones": {
            "valor_canon_sugerido": contrato.canon_mandato,
            "comision": contrato.comision_porcentaje_contrato_m,
            "duracion_meses": contrato.duracion_contrato_m,
            "fecha_pago": contrato.fecha_pago,
        }
    }
    return datos

from datetime import datetime

def repro_pdf_70():
    try:
        datos = get_datos_contrato_mandato(70)
        print("v Datos preparados")
        
        facade = ServicioPDFFacade()
        print("v Generando PDF...")
        pdf_path = facade.generar_contrato_elite(datos)
        print(f"v PDF generado en: {pdf_path}")
        
    except Exception as e:
        print(f"x ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    repro_pdf_70()
