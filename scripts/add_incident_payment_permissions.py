"""
Script para agregar permisos de plan de pago de incidentes.
Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.dominio.entidades.permiso import Permiso
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_permisos import RepositorioPermisos


def add_incident_payment_permissions():
    """Agrega permisos para planes de pago de incidentes."""
    repo = RepositorioPermisos(db_manager)
    permisos_existentes = repo.listar_permisos()
    
    # Permisos para el módulo de Incidentes
    new_permissions = [
        {
            "modulo": "Incidentes",
            "ruta": "/incidentes",
            "accion": "DEFINIR_PLAN_PAGO",
            "descripcion": "Definir plan de pago para incidentes aprobados",
            "categoria": "Gestión"
        },
        {
            "modulo": "Incidentes",
            "ruta": "/incidentes",
            "accion": "VER_ESTADO_PAGO",
            "descripcion": "Visualizar estado de pago de incidentes",
            "categoria": "Consulta"
        },
    ]
    
    # Permisos para el módulo de Liquidaciones
    liquidaciones_permissions = [
        {
            "modulo": "Liquidaciones",
            "ruta": "/liquidaciones",
            "accion": "SELECCIONAR_INCIDENTES",
            "descripcion": "Seleccionar incidentes para asociar a liquidaciones",
            "categoria": "Gestión"
        },
    ]
    
    all_permissions = new_permissions + liquidaciones_permissions
    
    permisos_creados = 0
    permisos_existentes_count = 0
    
    for p_info in all_permissions:
        modulo = p_info["modulo"]
        accion = p_info["accion"]
        
        # 1. Verificar existencia
        exists = False
        for p in permisos_existentes:
            if p.modulo == modulo and p.accion == accion:
                exists = True
                break
                
        if exists:
            print(f"⚠️ El permiso '{modulo}: {accion}' ya existe.")
            permisos_existentes_count += 1
            continue

        # 2. Crear
        permiso = Permiso(
            modulo=modulo,
            ruta=p_info["ruta"],
            accion=accion,
            descripcion=p_info["descripcion"],
            categoria=p_info["categoria"]
        )

        try:
            repo.crear_permiso(permiso)
            print(f"✅ Permiso '{modulo}: {accion}' creado exitosamente.")
            permisos_creados += 1
        except Exception as e:
            print(f"❌ Error al crear permiso '{modulo}: {accion}': {e}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Permisos creados: {permisos_creados}")
    print(f"   - Permisos existentes: {permisos_existentes_count}")
    print(f"   - Total procesados: {permisos_creados + permisos_existentes_count}")


if __name__ == "__main__":
    add_incident_payment_permissions()
