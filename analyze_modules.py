"""
Script para extraer información sobre la estructura de módulos y tablas del sistema.
"""
from src.infraestructura.persistencia.database import db_manager

def get_system_modules():
    """Obtiene los módulos del sistema basados en las páginas."""
    modules = {
        "Dashboard": "/dashboard",
        "Personas": "/personas",
        "Propiedades": "/propiedades",
        "Contratos": "/contratos",
        "Liquidaciones": "/liquidaciones",
        "Liquidación Asesores": "/liquidacion-asesores",
        "Recaudos": "/recaudos",
        "Desocupaciones": "/desocupaciones",
        "Incidentes": "/incidentes",
        "Seguros": "/seguros",
        "Saldos a Favor": "/saldos-favor",
        "Recibos Públicos": "/recibos-publicos",
        "IPC / Incrementos": "/incrementos",
        "Proveedores": "/proveedores",
        "Usuarios": "/usuarios",
        "Configuración": "/configuracion",
        "Auditoría": "/auditoria",
    }
    return modules

def get_permissions_tables():
    """Obtiene las tablas relacionadas con permisos."""
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # Buscar tablas de permisos
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%permiso%' OR table_name LIKE '%rol%')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        return [t[0] if isinstance(t, tuple) else list(t.values())[0] for t in tables]
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("=" * 60)
    print("MÓDULOS DEL SISTEMA")
    print("=" * 60)
    modules = get_system_modules()
    for i, (name, route) in enumerate(modules.items(), 1):
        print(f"{i:2d}. {name:25s} → {route}")
    
    print(f"\n{str(len(modules))} módulos en total")
    
    print("\n" + "=" * 60)
    print("TABLAS DE PERMISOS/ROLES")
    print("=" * 60)
    tables = get_permissions_tables()
    if tables:
        for table in tables:
            print(f"- {table}")
    else:
        print("No se encontraron tablas de permisos/roles")
