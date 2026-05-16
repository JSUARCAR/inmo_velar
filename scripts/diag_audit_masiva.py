import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_postgres import RepositorioAsesorPostgres
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import RepositorioContratoArrendamientoPostgres
from src.infraestructura.repositorios.repositorio_liquidacion_asesor import RepositorioLiquidacionAsesor

def run_audit():
    print("=== AUDITORÍA DE GENERACIÓN MASIVA ===")
    
    periodo = datetime.now().strftime("%Y-%m")
    print(f"Período de prueba: {periodo}")
    
    repo_asesor = RepositorioAsesorPostgres(db_manager)
    repo_ca = RepositorioContratoArrendamientoPostgres(db_manager)
    repo_liq = RepositorioLiquidacionAsesor(db_manager)
    
    asesores = repo_asesor.listar_activos()
    print(f"1. Asesores Activos: {len(asesores)}")
    for a in asesores:
        print(f"   - ID: {a.id_asesor}, Nombre: {a.nombre_completo}")
        
    agrupados = repo_ca.obtener_activos_todos_agrupados()
    print(f"2. Asesores con contratos agrupados: {len(agrupados)}")
    print(f"   Keys types: {[type(k) for k in agrupados.keys()][:5]}")
    
    print("3. Análisis de compatibilidad:")
    for a in asesores:
        # Check if already liquidated
        existente = repo_liq.obtener_por_asesor_periodo(a.id_asesor, periodo)
        liquidada = "SI" if existente else "NO"
        
        # Check if has active contracts
        contratos = agrupados.get(a.id_asesor, [])
        num_contratos = len(contratos)
        
        print(f"   - Asesor {a.id_asesor}: Liquidada={liquidada}, Contratos={num_contratos}")
        if not contratos and num_contratos == 0:
            # Check why no contracts?
            # List some raw data?
            pass

    # Check raw data in CONTRATOS_MANDATOS vs CONTRATOS_ARRENDAMIENTOS
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        cursor.execute("SELECT ID_CONTRATO_M, ID_PROPIEDAD, ID_ASESOR, ESTADO_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ESTADO_CONTRATO_M = 'Activo'")
        mandatos = cursor.fetchall()
        print(f"4. Mandatos Activos Raw: {len(mandatos)}")
        
        cursor.execute("SELECT ID_CONTRATO_A, ID_PROPIEDAD, ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'")
        arriendos = cursor.fetchall()
        print(f"5. Arrendamientos Activos Raw: {len(arriendos)}")
        
        # Cross check
        cursor.execute("""
            SELECT ca.ID_CONTRATO_A, cm.ID_ASESOR
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
            WHERE ca.ESTADO_CONTRATO_A = 'Activo'
              AND cm.ESTADO_CONTRATO_M = 'Activo'
        """)
        matches = cursor.fetchall()
        print(f"6. Matches Mandato/Arriendo: {len(matches)}")

if __name__ == "__main__":
    run_audit()
