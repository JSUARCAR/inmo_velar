"""
Script para inicializar los 68 permisos base del sistema.
Ejecutar una sola vez después de crear las tablas.
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.dominio.entidades.permiso import Permiso
from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_permisos import ServicioPermisos


# Definición de los 17 módulos del sistema con sus categorías
MODULOS_SISTEMA = [
    # Gestión
    {"modulo": "Dashboard", "ruta": "/dashboard", "categoria": "Analytics"},
    {"modulo": "Personas", "ruta": "/personas", "categoria": "Gesti\u00f3n"},
    {"modulo": "Propiedades", "ruta": "/propiedades", "categoria": "Gesti\u00f3n"},
    {"modulo": "Contratos", "ruta": "/contratos", "categoria": "Gesti\u00f3n"},
    {"modulo": "Proveedores", "ruta": "/proveedores", "categoria": "Gesti\u00f3n"},
    
    # Financiero
    {"modulo": "Liquidaciones", "ruta": "/liquidaciones", "categoria": "Financiero"},
    {"modulo": "Liquidaci\u00f3n Asesores", "ruta": "/liquidacion-asesores", "categoria": "Financiero"},
    {"modulo": "Recaudos", "ruta": "/recaudos", "categoria": "Financiero"},
    {"modulo": "Saldos a Favor", "ruta": "/saldos-favor", "categoria": "Financiero"},
    
    # Operaciones
    {"modulo": "Desocupaciones", "ruta": "/desocupaciones", "categoria": "Operaciones"},
    {"modulo": "Incidentes", "ruta": "/incidentes", "categoria": "Operaciones"},
    {"modulo": "Seguros", "ruta": "/seguros", "categoria": "Operaciones"},
    {"modulo": "Recibos P\u00fablicos", "ruta": "/recibos-publicos", "categoria": "Operaciones"},
    
    # Configuración
    {"modulo": "IPC / Incrementos", "ruta": "/incrementos", "categoria": "Configuraci\u00f3n"},
    
    # Administración
    {"modulo": "Usuarios", "ruta": "/usuarios", "categoria": "Administraci\u00f3n"},
    {"modulo": "Configuraci\u00f3n", "ruta": "/configuracion", "categoria": "Administraci\u00f3n"},
    {"modulo": "Auditor\u00eda", "ruta": "/auditoria", "categoria": "Administraci\u00f3n"},
]

# Las 4 acciones CRUD
ACCIONES = [
    {"accion": "VER", "descripcion": "Acceso a visualizar el m\u00f3dulo y sus datos"},
    {"accion": "CREAR", "descripcion": "Crear nuevos registros"},
    {"accion": "EDITAR", "descripcion": "Modificar registros existentes"},
    {"accion": "ELIMINAR", "descripcion": "Eliminar o desactivar registros"},
]


def inicializar_permisos():
    """
    Crea los 68 permisos base del sistema (17 módulos × 4 acciones).
    """
    
    print("=" * 70)
    print("INICIALIZACIÓN DE PERMISOS DEL SISTEMA")
    print("=" * 70)
    
    servicio = ServicioPermisos(db_manager)
    
    permisos_creados = 0
    permisos_existentes = 0
    errores = 0
    
    print(f"\nCreando permisos para {len(MODULOS_SISTEMA)} m\u00f3dulos...\n")
    
    for modulo_info in MODULOS_SISTEMA:
        modulo = modulo_info["modulo"]
        ruta = modulo_info["ruta"]
        categoria = modulo_info["categoria"]
        
        print(f"\n📦 {modulo} ({categoria})")
        
        for accion_info in ACCIONES:
            accion = accion_info["accion"]
            descripcion_base = accion_info["descripcion"]
            descripcion = f"{descripcion_base} en {modulo}"
            
            try:
                permiso = Permiso(
                    modulo=modulo,
                    ruta=ruta,
                    accion=accion,
                    descripcion=descripcion,
                    categoria=categoria
                )
                
                servicio.repo.crear_permiso(permiso)
                print(f"   ✅ {accion}")
                permisos_creados += 1
                
            except Exception as e:
                error_msg = str(e)
                if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print(f"   ⚠️  {accion} (ya existe)")
                    permisos_existentes += 1
                else:
                    print(f"   ❌ {accion}: {error_msg}")
                    errores += 1
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"✅ Permisos creados:    {permisos_creados}")
    print(f"⚠️  Permisos existentes: {permisos_existentes}")
    print(f"❌ Errores:             {errores}")
    print(f"📊 Total esperado:      {len(MODULOS_SISTEMA) * len(ACCIONES)} permisos")
    
    total_exitosos = permisos_creados + permisos_existentes
    if total_exitosos == len(MODULOS_SISTEMA) * len(ACCIONES):
        print("\n🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!")
        return True
    else:
        print(f"\n⚠️  ATENCIÓN: Se esperaban {len(MODULOS_SISTEMA) * len(ACCIONES)} permisos, se procesaron {total_exitosos}")
        return False


def listar_permisos_creados():
    """Lista todos los permisos creados para verificación."""
    servicio = ServicioPermisos(db_manager)
    
    print("\n" + "=" * 70)
    print("PERMISOS EN EL SISTEMA")
    print("=" * 70)
    
    permisos_agrupados = servicio.obtener_permisos_agrupados_por_categoria()
    
    for categoria, permisos in permisos_agrupados.items():
        print(f"\n{categoria}:")
        modulos = {}
        for p in permisos:
            if p.modulo not in modulos:
                modulos[p.modulo] = []
            modulos[p.modulo].append(p.accion)
        
        for modulo, acciones in modulos.items():
            acciones_str = ", ".join(sorted(acciones))
            print(f"  • {modulo}: {acciones_str}")


if __name__ == "__main__":
    try:
        print("\n🚀 Iniciando script de inicialización de permisos...\n")
        
        # 1. Inicializar permisos
        success = inicializar_permisos()
        
        # 2. Listar permisos creados
        listar_permisos_creados()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ SISTEMA DE PERMISOS LISTO PARA USAR")
            print("=" * 70)
            print("\nPróximos pasos:")
            print("1. Asignar permisos a roles usando la UI")
            print("2. O aplicar presets: python scripts/apply_preset.py")
            exit(0)
        else:
            print("\n⚠️  Revisa los errores arriba")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
